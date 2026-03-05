# 这就是你的一个 Skill（技能）
def get_weather(city: str) -> str:
    """获取指定城市的天气（模拟一个外部 API 请求）"""
    print(f"🔧 [Skill 被触发] 正在查询 {city} 的天气...")
    # 实际开发中这里会发起 HTTP 请求，比如 requests.get()
    weather_data = {
        "北京": "晴天，25度，适合外出",
        "上海": "阴天，20度，可能有小雨",
        "新加坡": "雷阵雨，30度，出门带伞",
    }
    return weather_data.get(city, "未知城市天气")


# Skill 的说明书
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海",
                    }
                },
                "required": ["city"],
            },
        },
    }
]



from openai import OpenAI
import os
from tools import get_weather, tools
import json

# 初始化你的 API 客户端 (这里以兼容 OpenAI 格式的 API 为例)
client = OpenAI(
    api_key="sk-ZsC8Pr2vB1MLjqHDm3xVF3LmuCLnN00JpLx5MjzQUMRgq61z",
    base_url="https://api.openai-proxy.org/v1",  # 如果用的是非 OpenAI 官方的模型，替换这里的 URL
)


def run_agent(user_input: str):
    messages = [{"role": "user", "content": user_input}]

    print(f"🧑‍💻 用户: {user_input}")

    # --- Agent 的核心 Workflow 循环 ---
    while True:
        print("🧠 [Agent 思考中...]")
        response = client.chat.completions.create(
            model="gpt-5-mini",  # 比如 gpt-3.5-turbo, qwen-max 等
            messages=messages,
            tools=tools,
            tool_choice="auto",  # 让大模型自己决定是否使用 Skill
        )

        response_message = response.choices[0].message

        # 判断 1：大模型是否决定调用 Skill？
        if response_message.tool_calls:
            messages.append(response_message)  # 把大模型的决定记录进历史

            # 遍历并执行大模型想要调用的 Skill
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                # 解析大模型提取的参数
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "get_weather":
                    # --- 这里是 Agent 真正“干活”的地方 ---
                    skill_result = get_weather(city=function_args.get("city"))

                    # 把干活的结果封装好，喂回给大模型
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": skill_result,
                        }
                    )
        else:
            # 判断 2：如果不需要调用 Skill，说明任务完成了，直接输出结果
            print(f"🤖 Agent: {response_message.content}")
            break  # 退出工作流


# 测试我们的 Agent
run_agent("我明天要去新加坡出差，那边天气怎么样？")
