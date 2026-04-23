```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 内存调度与架构演进 (多步交互版)</title>
    <style>
        :root {
            --bg-dark: #1e1e2e; --panel-bg: #282a36; --terminal-bg: #191a21;
            --text-main: #f8f8f2; --text-dim: #6272a4;
            --cyan: #8be9fd; --green: #50fa7b; --pink: #ff79c6;
            --orange: #ffb86c; --red: #ff5555; --yellow: #f1fa8c;
            --border-radius: 6px;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--bg-dark); color: var(--text-main);
            margin: 0; padding: 20px; line-height: 1.6;
        }
        h1, h2 { color: var(--cyan); border-bottom: 1px solid #44475a; padding-bottom: 10px; }
        .container { max-width: 1200px; margin: 0 auto; }
        
        .stage-card {
            background: var(--panel-bg); border-radius: var(--border-radius);
            padding: 25px; margin-bottom: 40px; box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            border-left: 6px solid var(--cyan); transition: all 0.3s;
        }
        .stage-card[data-stage="1"] { border-left-color: var(--red); }
        .stage-card[data-stage="2"] { border-left-color: var(--orange); }
        .stage-card[data-stage="3"] { border-left-color: var(--green); }
        .stage-card[data-stage="4"] { border-left-color: var(--pink); }

        .btn {
            background-color: #44475a; color: var(--text-main);
            border: 1px solid var(--cyan); padding: 10px 20px;
            border-radius: 4px; cursor: pointer; font-size: 15px;
            font-weight: bold; transition: all 0.2s; margin-bottom: 15px; margin-right: 10px;
        }
        .btn:hover:not(:disabled) { background-color: var(--cyan); color: #000; box-shadow: 0 0 10px var(--cyan); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; border-color: #6272a4; }

        .grid-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px; }
        .grid-3 { grid-template-columns: 1fr 1fr 1.5fr; }
        .full-width { grid-column: 1 / -1; }

        .panel {
            background: var(--terminal-bg); border-radius: var(--border-radius);
            padding: 15px; border: 1px solid #44475a; font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px; display: flex; flex-direction: column;
        }
        .panel-header {
            display: flex; justify-content: space-between; color: var(--pink);
            font-weight: bold; border-bottom: 1px dashed #44475a; padding-bottom: 8px;
            margin-bottom: 10px; margin-top: 0;
        }
        .scroll-area { flex-grow: 1; overflow-y: auto; max-height: 350px; }
        
        .log-entry { margin-bottom: 8px; padding: 6px; border-radius: 4px; background: #282a36; border-left: 3px solid; animation: fadeIn 0.3s ease; }
        .log-user { border-color: var(--green); }
        .log-ai { border-color: var(--cyan); }
        .log-sys { color: var(--text-dim); }

        .prompt-view { background: #000; border-color: var(--pink); color: var(--text-main); }
        .tag-xml { color: var(--pink); font-weight: bold; }
        pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }

        .highlight-loss { color: var(--red); text-decoration: line-through; }
        .highlight-keep { color: var(--green); font-weight: bold; }
        .log-dropped { color: var(--red); text-decoration: line-through; animation: fadeOut 2s forwards; }

        /* RAG Search Animation */
        .search-bar { display: flex; gap: 10px; margin-bottom: 15px; }
        .search-input { flex: 1; padding: 10px; background: var(--terminal-bg); border: 1px solid var(--cyan); color: white; border-radius: 4px; }
        .scanning { animation: scan 1s infinite alternate; color: var(--cyan); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scan { from { text-shadow: 0 0 5px var(--cyan); } to { text-shadow: 0 0 20px var(--cyan), 0 0 30px var(--cyan); } }
        @keyframes fadeOut { to { opacity: 0.3; } }
        @keyframes flash { 0%, 100% { background: transparent; } 50% { background: rgba(255,85,85,0.3); } }
    </style>
</head>
<body>

<div class="container">
    <h1>🔬 AI 架构演进：深度剖析“记忆”与“知识”</h1>
    <p>演示场景：排查一台 ESXi 主机 (10.0.0.51) 意外断开的真实排障全过程。</p>

    <div class="stage-card" data-stage="1">
        <h2>阶段一：裸机狂奔与 OOM (上下文腐化)</h2>
        <p>大模型原生状态下就像只有几十 KB 内存的设备。日志稍微多一点，早期排查记录就会被强行挤出内存，导致 AI "失忆"。你问它之前排查过什么，它开始胡编乱造。</p>
        <button class="btn" id="btn-s1" style="border-color: var(--red);">[模拟] 不断输入排障日志 (尾部追加)</button>
        <div class="panel" id="s1-ram">
            <h4 class="panel-header"><span>💾 L1 Cache (当前大模型上下文窗口)</span> <span id="s1-count">0/4 满载界限</span></h4>
            <div id="s1-content"></div>
        </div>
    </div>

    <div class="stage-card" data-stage="2">
        <h2>阶段二：初版 Memory —— 滚动摘要的“失真实验”</h2>
        <p>引入滑动窗口机制：保留最近 4 条日志，溢出的老日志会被 AI 压缩成“摘要”。<br>
        👉 <b>请不断点击下一步</b>，观察早期带具体 IP 和存储类型的对话是如何一步步被“磨损”掉的。</p>
        <button class="btn" id="btn-s2-next">下一轮对话 (+1)</button>
        <button class="btn" id="btn-s2-reset" style="background: transparent; border-color: var(--text-dim);">重置</button>
        
        <div class="grid-3">
            <div class="panel">
                <h4 class="panel-header">⏱️ 短期缓冲 (最多4条) <span id="s2-counter">0/4</span></h4>
                <div class="scroll-area" id="s2-buffer"></div>
            </div>
            <div class="panel">
                <h4 class="panel-header">📝 轨道一：历史快照 (滚动摘要)</h4>
                <div class="scroll-area" id="s2-summary" style="color: var(--orange);">[暂无摘要，等待溢出...]</div>
                <p style="color:var(--text-dim); font-size: 11px; margin-top: 10px;">注意观察：重要信息是否随着点击丢失？</p>
            </div>
            <div class="panel prompt-view">
                <h4 class="panel-header">⚙️ 实时发送给 LLM 的底层 Prompt</h4>
                <div class="scroll-area">
                    <pre id="s2-prompt" class="log-sys">点击开始排障推演...</pre>
                </div>
            </div>
        </div>
    </div>

    <div class="stage-card" data-stage="3">
        <h2>阶段三：终极 Memory —— 双轨制与 KV 状态机</h2>
        <p>为了对抗摘要带来的“信息磨损”，我们开启第二条轨道：<b>核心资产状态机</b>。它就像我们的 CMDB，强行提取关键设定并锁定为 JSON 格式。<br>
        👉 <b>继续点击</b>，这次有了左侧的“原生对话”作为参照，你能直观感受到：无论中间的摘要把 IP 丢弃得多干净，右侧的 KV 依然死死锁住底层逻辑！</p>
        <button class="btn" id="btn-s3-next">下一轮对话 (+1)</button>
        <button class="btn" id="btn-s3-reset" style="background: transparent; border-color: var(--text-dim);">重置剧本</button>
        
        <div class="grid-layout" style="grid-template-columns: repeat(3, 1fr);">
            <div class="panel">
                <h4 class="panel-header">⏱️ 短期缓冲 (对话现场) <span id="s3-counter">0/4</span></h4>
                <div class="scroll-area" id="s3-buffer"></div>
            </div>
            <div class="panel">
                <h4 class="panel-header">🗄️ 轨道二：CMDB (核心实体库)</h4>
                <div class="scroll-area">
                    <pre id="s3-kv" style="color: var(--yellow);">{}</pre>
                </div>
            </div>
            <div class="panel">
                <h4 class="panel-header">📝 轨道一：历史快照 (已失真)</h4>
                <div class="scroll-area" id="s3-summary" style="color: var(--text-dim);">[暂无摘要...]</div>
            </div>
            <div class="panel prompt-view full-width" >
                <h4 class="panel-header">⚙️ 融合了双轨的底层 Prompt</h4>
                <div class="scroll-area">
                    <pre id="s3-prompt" class="log-sys">点击开始双轨推演...</pre>
                </div>
            </div>
        </div>
    </div>

    <div class="stage-card" data-stage="4">
        <h2>阶段四：外挂存储 (RAG) 与完全体拼装</h2>
        <p>现在用户问了一个具体的命令。如果我们靠大模型的模糊记忆硬背，它很可能会捏造一个不存在的 ESXi 命令。我们现在通过 RAG 从外挂知识库中捞取原文档。</p>
        
        <div class="search-bar">
            <input type="text" class="search-input" value="查阅如何重启 vpxa 代理" disabled>
            <button class="btn" id="btn-s4-search" style="margin: 0;">触发向量检索</button>
        </div>
        
        <div id="rag-result" style="display: none; margin-bottom: 15px; color: var(--cyan); border-left: 3px solid var(--cyan); padding-left: 10px;">
            <div class="scanning">▶ 正在遍历 VMware 官方文档向量库...</div>
        </div>

        <div class="panel prompt-view">
            <h4 class="panel-header">🚀 AI 接收到的终极神级 XML Prompt</h4>
            <div class="scroll-area">
                <pre id="s4-prompt" class="log-sys">等待检索与生成...</pre>
            </div>
        </div>
    </div>
</div>

<script>
    // 剧本数据：长达13轮的排障对话
    const dialogueScript = [
        { role: 'user', text: "生产环境 ESXi 主机 10.0.0.51 在 vCenter 里无响应了。" },
        { role: 'ai', text: "收到，请确认底层 FC-SAN 存储链路状态。" },
        { role: 'user', text: "存储组看过了，链路全是 active 的。" },
        { role: 'ai', text: "网络能 Ping 通管理口吗？" },
        { role: 'user', text: "可以 Ping 通，SSH 也能进去。" }, // 5 触发第一次压缩
        { role: 'ai', text: "网络和存储正常，查一下 /var/log/vpxa.log。" },
        { role: 'user', text: "里面全都是 Request timeout 报错。" },
        { role: 'ai', text: "明白了，基本确认是 vpxa 管理代理卡死了。" }, // 8
        { role: 'user', text: "那我现在该怎么办？直接物理重启机器吗？" },
        { role: 'ai', text: "千万不要物理重启，可能会导致虚机损坏。" }, // 10
        { role: 'user', text: "那重启代理服务会影响上面跑的业务吗？" },
        { role: 'ai', text: "不会影响数据流量，只会短暂中断管理面。" },
        { role: 'user', text: "好的，我该敲什么命令重启？" } // 13
    ];

    // 预设的滚动摘要演进（演示信息磨损）
    const summaryEvolution = [
        "[暂无摘要，等待溢出...]", // 0-4
        "[快照更新] 开始排查 10.0.0.51 掉线。确认 FC-SAN 正常。", // 5-6
        "[快照更新] 排查 10.0.0.51。存储正常，网络可 Ping，排查日志中。", // 7-8 (丢失了FC-SAN细节)
        "[快照更新] 排查主机掉线。排除网络/存储故障，确认 vpxa 卡死，正在讨论修复方案。", // 9-10 (致命：10.0.0.51 丢失！)
        "<span class='highlight-loss'>[严重失真] 某主机服务卡死，正在讨论重启的安全影响。</span>" // 11-13 (完全失去上下文)
    ];

    // 预设的 KV 演进（绝对精准）
    const kvEvolution = [
        {}, // 0
        { "Target_IP": "10.0.0.51" }, // 1
        { "Target_IP": "10.0.0.51", "Storage": "FC-SAN" }, // 2
        { "Target_IP": "10.0.0.51", "Storage": "FC-SAN", "Fault_Component": "vpxa_agent" }, // 8
    ];

    // 工具函数：XML 高亮
    function formatXML(text) {
        return text.replace(/<(\/?[a-zA-Z_]+)>/g, '<span class="tag-xml"><$1></span>');
    }

    // --- 阶段 1：模拟 OOM ---
    const logs = [
        "[09:00] 收到告警，开始排查 10.0.0.51 掉线问题。",
        "[09:05] 执行 esxcli network ip ping，网络连通性正常。",
        "[09:10] 检查存储链路，FC-SAN 多路径显示 active。",
        "[09:15] 查看 /var/log/vpxa.log，发现大量 timeout 报错。",
        "[09:20] 尝试 SSH 登录宿主机，可以成功连入。"
    ];
    let s1Index = 0;
    const s1Content = document.getElementById('s1-content');
    const s1Count = document.getElementById('s1-count');
    
    document.getElementById('btn-s1').addEventListener('click', function() {
        if (s1Index >= logs.length) return;
        
        // 如果超过4条，最早的一条开始腐化
        if (s1Content.children.length >= 4) {
            s1Content.children[0].className = 'log-entry log-dropped';
            s1Content.children[0].innerText += " (已被挤出内存！)";
            setTimeout(() => { s1Content.removeChild(s1Content.children[0]); }, 2000);
            s1Content.parentElement.style.animation = 'flash 0.5s';
        }

        const div = document.createElement('div');
        div.className = 'log-entry log-user';
        div.innerText = logs[s1Index];
        s1Content.appendChild(div);
        
        s1Index++;
        s1Count.innerText = `${Math.min(s1Content.children.length, 4)}/4 满载界限`;
        
        if (s1Index === logs.length) this.disabled = true;
    });

    // --- 阶段二逻辑 ---
    let s2Index = 0;
    let s2BufferArr = [];
    const btnS2Next = document.getElementById('btn-s2-next');
    
    function updateS2View() {
        // 更新 Buffer
        const bufferDiv = document.getElementById('s2-buffer');
        bufferDiv.innerHTML = s2BufferArr.map(msg => 
            `<div class="log-entry ${msg.role === 'user' ? 'log-user' : 'log-ai'}">${msg.role.toUpperCase()}: ${msg.text}</div>`
        ).join('');
        document.getElementById('s2-counter').innerText = `${s2BufferArr.length}/4`;
        bufferDiv.scrollTop = bufferDiv.scrollHeight;

        // 计算当前摘要层级
        let summaryLevel = 0;
        if (s2Index >= 5) summaryLevel = 1;
        if (s2Index >= 7) summaryLevel = 2;
        if (s2Index >= 9) summaryLevel = 3;
        if (s2Index >= 11) summaryLevel = 4;
        
        const currentSummary = summaryEvolution[summaryLevel];
        document.getElementById('s2-summary').innerHTML = currentSummary;

        // 生成 Prompt
        const rawPrompt = `<System>你是一个运维助手。</System>\n\n<Rolling_Summary>\n${currentSummary.replace(/<[^>]+>/g, '')}\n</Rolling_Summary>\n\n<Recent_Buffer>\n${s2BufferArr.map(m=>m.role+": "+m.text).join('\n')}\n</Recent_Buffer>`;
        document.getElementById('s2-prompt').innerHTML = formatXML(rawPrompt);
    }

    btnS2Next.addEventListener('click', () => {
        if (s2Index < dialogueScript.length) {
            s2BufferArr.push(dialogueScript[s2Index]);
            if (s2BufferArr.length > 4) {
                s2BufferArr.shift(); // 踢出最早的
            }
            s2Index++;
            updateS2View();
        }
        if (s2Index >= dialogueScript.length) btnS2Next.disabled = true;
    });

    document.getElementById('btn-s2-reset').addEventListener('click', () => {
        s2Index = 0; s2BufferArr = []; btnS2Next.disabled = false; updateS2View();
    });

    // ==========================================
    // 阶段三逻辑 (更新：加入了对话缓冲面板)
    // ==========================================
    let s3Index = 0;
    let s3BufferArr = [];
    const btnS3Next = document.getElementById('btn-s3-next');

    function updateS3View() {
        // 1. 更新 Buffer 剧本面板
        s3BufferArr.push(dialogueScript[s3Index]);
        if (s3BufferArr.length > 4) s3BufferArr.shift();
        
        const bufferDiv = document.getElementById('s3-buffer');
        bufferDiv.innerHTML = s3BufferArr.map(msg => 
            `<div class="log-entry ${msg.role === 'user' ? 'log-user' : 'log-ai'}">${msg.role.toUpperCase()}: ${msg.text}</div>`
        ).join('');
        document.getElementById('s3-counter').innerText = `${s3BufferArr.length}/4`;
        bufferDiv.scrollTop = bufferDiv.scrollHeight;

        // 2. 更新 摘要 面板
        let summaryLevel = 0;
        if (s3Index >= 5) summaryLevel = 1;
        if (s3Index >= 7) summaryLevel = 2;
        if (s3Index >= 9) summaryLevel = 3;
        if (s3Index >= 11) summaryLevel = 4;
        const currentSummary = summaryEvolution[summaryLevel];
        document.getElementById('s3-summary').innerHTML = currentSummary;

        // 3. 更新 KV 状态机 面板
        let currentKV = kvEvolution[0];
        if (s3Index >= 1) currentKV = kvEvolution[1];
        if (s3Index >= 2) currentKV = kvEvolution[2];
        if (s3Index >= 8) currentKV = kvEvolution[3];
        document.getElementById('s3-kv').innerText = JSON.stringify(currentKV, null, 2);

        // 4. 生成双轨 Prompt 面板
        const rawPrompt = `<System>你是高级架构师。严格遵循 CMDB 资产信息，不能偏离！</System>\n\n<CMDB_Entities_KV>\n${JSON.stringify(currentKV, null, 2)}\n</CMDB_Entities_KV>\n\n<Macro_Summary>\n${currentSummary.replace(/<[^>]+>/g, '')}\n</Macro_Summary>\n\n<Recent_Buffer>\n${s3BufferArr.map(m=>m.role+": "+m.text).join('\n')}\n</Recent_Buffer>`;
        
        const promptEl = document.getElementById('s3-prompt');
        promptEl.innerHTML = formatXML(rawPrompt);
        
        // 特别高亮：让听众看到即使摘要丢了 IP，KV 里依然有
        if (summaryLevel >= 3) {
            promptEl.innerHTML = promptEl.innerHTML.replace('"10.0.0.51"', '<span class="highlight-keep">"10.0.0.51" (强力锁定!)</span>');
        }

        s3Index++;
        if (s3Index >= dialogueScript.length) btnS3Next.disabled = true;
    }

    btnS3Next.addEventListener('click', updateS3View);
    
    document.getElementById('btn-s3-reset').addEventListener('click', () => {
        s3Index = 0; s3BufferArr = []; btnS3Next.disabled = false; 
        document.getElementById('s3-buffer').innerHTML = '';
        document.getElementById('s3-counter').innerText = '0/4';
        document.getElementById('s3-kv').innerText = '{}';
        document.getElementById('s3-summary').innerHTML = '[暂无摘要...]';
        document.getElementById('s3-prompt').innerHTML = '点击开始双轨推演...';
    });

    // --- 阶段四：RAG 与完全体 ---
    document.getElementById('btn-s4-search').addEventListener('click', function() {
        this.disabled = true;
        const resultDiv = document.getElementById('rag-result');
        const promptDiv = document.getElementById('s4-prompt');
        
        resultDiv.style.display = 'block';
        
        setTimeout(() => {
            resultDiv.innerHTML = `✅ <b>命中 VMware KB 知识库:</b> <br><br>当需重启 ESXi 代理服务而不影响虚机时，请通过 SSH 执行：<br><code>/etc/init.d/vpxa restart</code>`;
            
            // 组装神级 Prompt，使用打字机效果
            const finalPrompt = `<System_Instruction>
你是一个高级全栈 Infra 架构师。
要求：
1. 你的目标资产必须且只能是 <CMDB_Entities> 里的 IP。
2. 修复操作必须严格依据 <RAG_Retrieved_Docs>，禁止捏造命令。
</System_Instruction>

<CMDB_Entities>
{
  "Target_IP": "10.0.0.51",
  "Storage": "FC-SAN",
  "Fault_Component": "vpxa_agent"
}
</CMDB_Entities>

<Troubleshooting_Summary>
某主机服务卡死，正在讨论重启的安全影响。
</Troubleshooting_Summary>

<RAG_Retrieved_Docs>
【VMware KB-1003490】
当需重启 ESXi 代理服务而不影响虚机数据流量时，请通过 SSH 登录执行：
/etc/init.d/vpxa restart
</RAG_Retrieved_Docs>

<Recent_Buffer>
User: 好的，我该敲什么命令重启？
</Recent_Buffer>

Assistant: `;
            
            promptDiv.innerHTML = "";
            let i = 0;
            let typeTimer = setInterval(() => {
                promptDiv.innerHTML += finalPrompt.charAt(i);
                i++;
                if (i >= finalPrompt.length) {
                    clearInterval(typeTimer);
                    promptDiv.innerHTML = formatXML(finalPrompt);
                    // 高亮终极输出
                    promptDiv.innerHTML += `<br><br><span style="color:var(--green)">[AI 实际输出预判]：根据手册，请您 SSH 登录到 <b>10.0.0.51</b>，并执行命令 <b>/etc/init.d/vpxa restart</b>。</span>`;
                }
            }, 5);

        }, 1500); // 模拟 1.5 秒的网络检索延迟
    });
</script>

</body>
</html>
```
