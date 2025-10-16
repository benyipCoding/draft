```python
# workflow_engine.py
import time
import threading
import concurrent.futures
from typing import Dict, List, Any, Callable, Optional
import traceback

# -------------------------
# 任务/决策函数注册区 (示例)
# -------------------------
def prepare_env(params):
    name = params.get("name", "prepare_env")
    print(f"[{time.strftime('%X')}] prepare_env start ({name})")
    time.sleep(0.5)
    print(f"[{time.strftime('%X')}] prepare_env done ({name})")
    return {"status": "ok"}

def run_main_test(params):
    name = params.get("name", "run_main_test")
    print(f"[{time.strftime('%X')}] run_main_test start ({name})")
    time.sleep(1.0)
    print(f"[{time.strftime('%X')}] run_main_test done ({name})")
    return {"status": "ok"}

def check_dependencies(params):
    name = params.get("name", "check_dependencies")
    # 模拟一个失败/成功切换，通过params控制
    result = params.get("result", "fail")  # "fail" or "pass"
    print(f"[{time.strftime('%X')}] check_dependencies ({name}) -> {result}")
    return result

def decide_if_success(params):
    # 假设上游把 dependencies 的结果放到 params 中
    dep_result = params.get("dep_result")
    # 也可以读取动态上下文，这里简单处理
    ok = dep_result == "pass"
    print(f"[{time.strftime('%X')}] decide_if_success -> {ok}")
    return ok

def generate_report(params):
    print(f"[{time.strftime('%X')}] generate_report start")
    time.sleep(0.3)
    print(f"[{time.strftime('%X')}] generate_report done")
    return {"report": "ok"}

# 注册函数表
REGISTERED_FUNCS: Dict[str, Callable[[Dict[str, Any]], Any]] = {
    "prepare_env": prepare_env,
    "run_main_test": run_main_test,
    "check_dependencies": check_dependencies,
    "decide_if_success": decide_if_success,
    "generate_report": generate_report,
}

# -------------------------
# WorkflowEngine
# -------------------------
class WorkflowEngine:
    def __init__(self, wf_json: Dict[str, Any], max_workers: int = 8, max_exec_per_node: int = 10):
        """
        wf_json:
            {
              "nodes": [ {"id": str, "type": "start|task|decision|end", "func": optional, "params": {...}}, ... ],
              "edges": [ {"from": id, "to": id, "condition": optional}, ... ]
            }
        """
        self.nodes = {n["id"]: n.copy() for n in wf_json["nodes"]}
        self.edges = [e.copy() for e in wf_json["edges"]]

        # Build adjacency structures
        self.successors: Dict[str, List[Dict[str, Any]]] = {nid: [] for nid in self.nodes}
        self.predecessors: Dict[str, List[Dict[str, Any]]] = {nid: [] for nid in self.nodes}
        for e in self.edges:
            f = e["from"]
            t = e["to"]
            self.successors[f].append(e)
            self.predecessors[t].append(e)

        # Detect back-edges (simple DFS classification). Mark edges with key "_is_back_edge": True/False
        self._mark_back_edges()

        # required_tokens = number of incoming edges excluding back-edges (so initial firing won't wait for loop back-edges)
        self.required_tokens: Dict[str, int] = {
            nid: sum(1 for e in self.predecessors[nid] if not e.get("_is_back_edge", False))
            for nid in self.nodes
        }

        # token counters (runtime): how many tokens have arrived for this node in the current "activation window"
        self.tokens_received: Dict[str, int] = {nid: 0 for nid in self.nodes}

        # bookkeeping
        self.lock = threading.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, concurrent.futures.Future] = {}  # active futures for logging/wait
        self.node_exec_counts: Dict[str, int] = {nid: 0 for nid in self.nodes}
        self.max_exec_per_node = max_exec_per_node

        # results and context
        self.results: Dict[str, Any] = {}   # node_id -> last result or exception
        self.context: Dict[str, Any] = {}   # workflow-level context for passing values between nodes

    # -------------------------
    # Back-edge detection (DFS)
    # -------------------------
    def _mark_back_edges(self):
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in self.nodes}

        def dfs(u):
            color[u] = GRAY
            for e in self.successors[u]:
                v = e["to"]
                if color[v] == WHITE:
                    dfs(v)
                elif color[v] == GRAY:
                    # found a back-edge u->v (cycle)
                    e["_is_back_edge"] = True
                # else BLACK: forward/cross edge - do nothing
            color[u] = BLACK

        # run DFS from all nodes (to cover disconnected)
        for nid in self.nodes:
            if color[nid] == WHITE:
                dfs(nid)
        # For edges not marked, set False
        for e in self.edges:
            if "_is_back_edge" not in e:
                e["_is_back_edge"] = False

    # -------------------------
    # Start the workflow
    # -------------------------
    def start(self, wait: bool = True):
        # initialize: tokens_received = 0 already
        # seed tokens for nodes that have required_tokens == 0 (start nodes)
        with self.lock:
            ready_nodes = [nid for nid, req in self.required_tokens.items() if req == 0]
            for nid in ready_nodes:
                # directly schedule as if they received enough tokens
                self._schedule_node(nid)

        if wait:
            # wait for all scheduled tasks to finish
            # we wait until the executor has no running futures (simple approach)
            while True:
                with self.lock:
                    active = [f for f in self.futures.values() if not f.done()]
                if not active:
                    break
                time.sleep(0.1)
            # allow a small time for any final callbacks
            time.sleep(0.1)
            print("Workflow finished. Node results summary:")
            for nid, res in self.results.items():
                print(f"  {nid}: {res}")

    # -------------------------
    # Node scheduling & execution
    # -------------------------
    def _schedule_node(self, node_id: str):
        # schedule but check exec limit
        if self.node_exec_counts[node_id] >= self.max_exec_per_node:
            print(f"[WARN] node {node_id} reached max executions ({self.max_exec_per_node}), skipping further runs.")
            return
        if node_id in self.futures and not self.futures[node_id].done():
            # already running; do not schedule duplicate
            return
        # submit
        fut = self.executor.submit(self._run_node, node_id)
        self.futures[node_id] = fut

    def _run_node(self, node_id: str):
        node = self.nodes[node_id]
        ntype = node.get("type", "task")
        func_name = node.get("func")
        params = dict(node.get("params", {}))  # copy to avoid mutation
        self.node_exec_counts[node_id] += 1

        try:
            # For decision nodes, it's common to want access to context
            if ntype == "task":
                if func_name:
                    fn = REGISTERED_FUNCS.get(func_name)
                    if not fn:
                        raise RuntimeError(f"Task func '{func_name}' not registered")
                    res = fn({**params, **self._gather_context_for(node_id)})
                else:
                    print(f"[{time.strftime('%X')}] task {node_id} no-op")
                    res = None
            elif ntype == "decision":
                if func_name:
                    fn = REGISTERED_FUNCS.get(func_name)
                    if not fn:
                        raise RuntimeError(f"Decision func '{func_name}' not registered")
                    # decision functions may need context (e.g., check_dependencies result)
                    res = fn({**params, **self._gather_context_for(node_id)})
                else:
                    # use params['route'] if provided
                    res = params.get("route")
            elif ntype == "start":
                print(f"[{time.strftime('%X')}] start node {node_id}")
                res = None
            elif ntype == "end":
                print(f"[{time.strftime('%X')}] end node {node_id}")
                res = None
            else:
                print(f"[{time.strftime('%X')}] unknown node type {ntype} for {node_id}, treated as no-op")
                res = None

            # store result into results and optional context (merge simple values)
            with self.lock:
                self.results[node_id] = {"success": True, "value": res}
                # simple merging strategy: if res is dict, merge into context under node_id
                if isinstance(res, dict):
                    # store per-node outputs under context[node_id]
                    self.context[node_id] = res
                else:
                    self.context[node_id] = res

            # on success, propagate tokens along outgoing edges according to conditions
            self._propagate_tokens(node_id, success=True, result=res)
            return res

        except Exception as exc:
            tb = traceback.format_exc()
            print(f"[{time.strftime('%X')}] node {node_id} raised exception:\n{tb}")
            with self.lock:
                self.results[node_id] = {"success": False, "error": str(exc)}
            # on failure, you might choose to propagate failure tokens or halt; here we stop propagation along this node's edges
            # But we still call propagate with success=False to allow custom behavior if desired
            self._propagate_tokens(node_id, success=False, result=exc)
            return exc

    # Helper to provide context inputs to functions (example)
    def _gather_context_for(self, node_id: str) -> Dict[str, Any]:
        # This function can be extended: provide upstream data, last results, etc.
        # For demo: provide the entire context and last results
        return {
            "workflow_context": dict(self.context),
            "last_results": dict(self.results)
        }

    # -------------------------
    # Token propagation
    # -------------------------
    def _propagate_tokens(self, from_node: str, success: bool, result: Any):
        """
        For each outgoing edge of from_node:
          - If edge is decision-guarded, check conditions.
          - If chosen, increment tokens_received[target] by 1.
          - If tokens_received[target] >= required_tokens[target], schedule target and reset its token counter (for next activation).
        """
        with self.lock:
            out_edges = list(self.successors.get(from_node, []))
        taken_edges = []
        node = self.nodes[from_node]
        if not out_edges:
            return

        for e in out_edges:
            # condition checking
            cond = e.get("condition", None)
            take = False
            if node.get("type") == "decision":
                # for decision nodes, compare result to edge.condition
                # treat boolean/str/int naturally; exact match
                if cond is None:
                    take = True
                else:
                    # for booleans, edge condition might be True/False; compare accordingly
                    take = (result == cond)
            else:
                # non-decision: take all outgoing edges
                take = True

            if take:
                taken_edges.append(e)

        # Propagate tokens for taken edges
        for e in taken_edges:
            to_n = e["to"]
            with self.lock:
                self.tokens_received[to_n] += 1
                tr = self.tokens_received[to_n]
                req = self.required_tokens.get(to_n, 0)
                print(f"[{time.strftime('%X')}] token: {from_node} -> {to_n}  (tokens={tr} / required={req}) (back_edge={e.get('_is_back_edge')})")
                # If enough tokens received, schedule node and reset tokens_received for that node
                if tr >= req:
                    # reset tokens_received for that node (ready for next activation cycle)
                    self.tokens_received[to_n] = 0
                    # but respect max exec count
                    if self.node_exec_counts[to_n] >= self.max_exec_per_node:
                        print(f"[WARN] not scheduling {to_n} because exec_count reached limit")
                    else:
                        self._schedule_node(to_n)

    # -------------------------
    # Utility: pretty print graph info
    # -------------------------
    def debug_print(self):
        print("Nodes:")
        for nid, n in self.nodes.items():
            print(f"  {nid}: type={n.get('type')} func={n.get('func')} required_tokens={self.required_tokens[nid]}")
        print("Edges:")
        for e in self.edges:
            print(f"  {e['from']} -> {e['to']} cond={e.get('condition')} back={e.get('_is_back_edge')}")

# -------------------------
# 示例工作流 (符合用户要求的复杂示例)
# -------------------------
EXAMPLE_WF = {
    "nodes": [
        {"id": "Start", "type": "start"},
        {"id": "A", "type": "task", "func": "prepare_env", "params": {"name": "A"}},
        {"id": "B", "type": "task", "func": "run_main_test", "params": {"name": "B"}},
        {"id": "C", "type": "task", "func": "check_dependencies", "params": {"name": "C", "result": "fail"}},  # set "fail" to force loop once
        {"id": "E", "type": "decision", "func": "decide_if_success"},  # decision node: True -> D, False -> A (loop)
        {"id": "D", "type": "task", "func": "generate_report"},
        {"id": "End", "type": "end"},
    ],
    "edges": [
        {"from": "Start", "to": "A"},
        {"from": "A", "to": "B"},
        {"from": "A", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "E"},
        {"from": "E", "to": "D", "condition": True},
        {"from": "E", "to": "A", "condition": False},  # loop back to A on False
        {"from": "D", "to": "End"},
    ]
}

# -------------------------
# Run demo if executed as script
# -------------------------
if __name__ == "__main__":
    print("Building engine and printing graph info...")
    engine = WorkflowEngine(EXAMPLE_WF, max_workers=4, max_exec_per_node=5)
    engine.debug_print()
    print("\nStarting workflow run (first run: C returns 'fail' causing E -> A loop).")
    engine.start(wait=True)

    # After first run complete, change C to pass and run again (demonstrate loop exit)
    print("\n--- Second run: make C pass so decision goes to D ---")
    # update node C's params to pass
    engine.nodes["C"]["params"]["result"] = "pass"
    # reset runtime counters for demonstration (in real system you'd create a fresh engine or persist state)
    engine.tokens_received = {nid: 0 for nid in engine.nodes}
    engine.node_exec_counts = {nid: 0 for nid in engine.nodes}
    engine.results = {}
    engine.context = {}
    engine.futures = {}
    engine.start(wait=True)


```
