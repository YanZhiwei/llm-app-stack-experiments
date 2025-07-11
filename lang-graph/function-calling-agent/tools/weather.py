"""
天气查询工具 - 获取城市天气信息
"""

from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息（使用搜索获取）"""
    try:
        # 使用搜索获取天气信息
        query = f"{city} 天气 今天"
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if results:
            weather_info = []
            for result in results:
                if '天气' in result.get('title', '') or '气温' in result.get('body', ''):
                    weather_info.append(f"• {result.get('title', '')}\n  {result.get('body', '')[:150]}...")
            
            if weather_info:
                return f"{city} 天气信息:\n\n" + "\n\n".join(weather_info)
            else:
                return f"未找到 {city} 的详细天气信息，建议使用更具体的城市名称"
        else:
            return f"无法获取 {city} 的天气信息"
    except Exception as e:
        return f"获取天气信息失败: {str(e)}" 