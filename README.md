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
