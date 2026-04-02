import json
import copy
import os
import random
from dataclasses import dataclass
from openai import OpenAI


# ==========================================
# 1. 定义状态快照 (ESXi 集群的全局 State)
# ==========================================
@dataclass
class ESXiState:
    host_name: str = "esxi-prod-01"
    vcenter_status: str = "NOT_RESPONDING"  # vCenter 视角的告警状态
    is_ssh_connected: bool = False  # SSH 是否已连上
    hung_vms_count: int = 1  # 僵死的虚拟机数量
    issue_resolved: bool = False  # 问题是否已解决
    last_action_result: str = (
        "🚨 告警触发：vCenter 报告 esxi-prod-01 主机无响应，且上面有 1 台核心业务 VM 处于僵死状态。请立即排查！"
    )


# ==========================================
# 2. 状态更新引擎 (模拟真实且混沌的运维环境)
# ==========================================
def reducer(state: ESXiState, action: dict) -> ESXiState:
    new_state = copy.deepcopy(state)
    action_type = action.get("type")

    if not action_type:
        new_state.last_action_result = "❌ 执行失败：指令解析异常！"
        return new_state

    # 动作 1：尝试 SSH 连接主机
    if action_type == "CONNECT_SSH":
        # 模拟生产环境的随机性：有概率连不上
        outcome = random.choice(["success", "timeout", "auth_fail"])
        if outcome == "success":
            new_state.is_ssh_connected = True
            new_state.last_action_result = (
                f"✅ SSH 登录成功：已获取 {state.host_name} 的 root 终端权限。"
            )
        elif outcome == "timeout":
            new_state.last_action_result = f"❌ SSH 超时：{state.host_name} 管理网络无响应，可能 hostd 已经彻底卡死。"
        else:
            new_state.last_action_result = f"❌ SSH 认证失败：密码可能已被修改或锁定。"

    # 动作 2：杀掉僵死的虚拟机
    elif action_type == "KILL_HUNG_VM":
        if not state.is_ssh_connected:
            new_state.last_action_result = (
                "⚠️ 权限拒绝：必须先通过 CONNECT_SSH 连入主机才能执行 esxcli 命令！"
            )
        else:
            outcome = random.choice(["success", "force_required", "world_not_found"])
            if outcome == "success":
                new_state.hung_vms_count -= 1
                new_state.last_action_result = "✅ esxcli vm process kill 执行成功：僵死 VM 已被软杀掉 (soft kill)。"
            elif outcome == "force_required":
                new_state.last_action_result = "❌ 杀进程失败：soft 模式无效，VM 进程组已被 vmkernel 锁死，建议稍后尝试强制重启管理服务。"
            else:
                new_state.last_action_result = "⚠️ 找不到进程：esxcli 没有列出该 VM 的 World ID，可能底层存储已经断开。"

    # 动作 3：重启 ESXi 管理代理 (services.sh restart)
    elif action_type == "RESTART_MANAGEMENT_AGENTS":
        if not state.is_ssh_connected:
            new_state.last_action_result = "⚠️ 权限拒绝：必须先连入 SSH！"
        else:
            outcome = random.choice(["success", "hostd_hung"])
            if outcome == "success":
                new_state.vcenter_status = "CONNECTED"
                new_state.issue_resolved = True
                new_state.last_action_result = "✅ services.sh restart 执行完毕：hostd 和 vpxa 已经重启，vCenter 恢复了对主机的连接！"
            else:
                new_state.last_action_result = "❌ 重启服务卡死：/etc/init.d/hostd restart 卡住，无法释放资源。主机可能需要按电源键硬重启 (Hard Reset)。"

    # 动作 4：升级给人类 L3 工程师
    elif action_type == "ESCALATE_TO_HUMAN":
        new_state.issue_resolved = True
        new_state.last_action_result = f"📞 已升级至 L3 工程师处理，Agent 移交控制权。交接原因：{action.get('reason', '无')}"

    # 动作 5：完结工单
    elif action_type == "RESOLVE_TICKET":
        if new_state.vcenter_status == "CONNECTED" and new_state.hung_vms_count == 0:
            new_state.last_action_result = (
                "🎉 工单关闭：主机已恢复连接，且僵死虚拟机已清理。"
            )
        else:
            new_state.last_action_result = (
                "⚠️ 拒绝关闭：主机未恢复或仍有僵死 VM，请勿提前关闭工单！"
            )

    else:
        new_state.last_action_result = f"⚠️ 未知的运维脚本: {action_type}"

    return new_state


# ==========================================
# 3. 大模型调度层 (运维 Agent 的大脑)
# ==========================================
def call_llm_brain(state: ESXiState, client: OpenAI) -> dict:
    system_prompt = """
    你是一个资深的 VMware ESXi L2 自动化运维 Agent。
    你的目标是排查并修复当前 ESXi 主机的告警状态，尽可能让其恢复到 CONNECTED 状态，并处理僵死的 VM。
    
    你必须根据当前传入的【服务器状态】，思考最优的排障步骤。遇到报错时，你需要分析原因并尝试其他手段。
    如果你发现所有手段都用尽，或者主机处于需要硬重启等物理干预的死锁状态，你必须升级给人类。
    
    你只能执行以下五种动作之一：
    1. CONNECT_SSH (尝试通过 SSH 连入主机)
    2. KILL_HUNG_VM (尝试使用 esxcli 杀掉僵死的虚拟机)
    3. RESTART_MANAGEMENT_AGENTS (执行 services.sh restart 重启管理网络)
    4. ESCALATE_TO_HUMAN (升级给人类，需提供 reason)
    5. RESOLVE_TICKET (当主机恢复连接且僵死 VM 为 0 时调用，完结工单)

    【严格要求】
    仅输出合法的 JSON，不要输出 Markdown 标记或解释。格式如下：
    {
        "thought": "你的排障思路，分析上一步的执行结果，并决定下一步策略",
        "type": "CONNECT_SSH | KILL_HUNG_VM | RESTART_MANAGEMENT_AGENTS | ESCALATE_TO_HUMAN | RESOLVE_TICKET",
        "reason": "仅在调用 ESCALATE 动作时填写原因"
    }
    """

    user_prompt = (
        f"当前 ESXi 状态：\n{json.dumps(state.__dict__, ensure_ascii=False, indent=2)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        return {"thought": "解析异常", "type": "ERROR", "reason": str(e)}


# ==========================================
# 4. 自动化运维流 (Agent REPL Loop)
# ==========================================
def agent_loop():
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url="https://api.openai-proxy.org/v1",
    )
    current_state = ESXiState()
    max_steps = 8

    print("🤖 ESXi 自动化运维 Agent 启动...")

    for step in range(1, max_steps + 1):
        print(f"\n{'='*20} 🔄 第 {step} 轮排障 {'='*20}")
        print(
            f"📡 监控面板快照:\n   vCenter: {current_state.vcenter_status} | SSH: {current_state.is_ssh_connected} | 僵死VM: {current_state.hung_vms_count}"
        )
        print(f"   上一步终端回显: {current_state.last_action_result}")

        # 1. 观察与规划
        print("\n🧠 Agent 日志分析与诊断中...")
        action = call_llm_brain(current_state, client)

        print(f"💡 思考 (CoT): {action.get('thought', '')}")
        print(f"🛠️  执行动作: {action.get('type')}")

        # 2. 检查是否主动终止 (修复或升级)
        if action.get("type") in ["RESOLVE_TICKET", "ESCALATE_TO_HUMAN"]:
            if action.get("type") == "ESCALATE_TO_HUMAN":
                print(f"\n🚨 任务移交人类。移交说明: {action.get('reason')}")
            else:
                print("\n✅ 工单已成功自动关闭！")
            break

        # 3. 执行更新 (还原环境的真实反馈)
        current_state = reducer(current_state, action)

        if step == max_steps:
            print("\n⚠️ 触发安全熔断：Agent 排障步数超限，自动停止以防引起次生灾害！")


if __name__ == "__main__":
    agent_loop()
