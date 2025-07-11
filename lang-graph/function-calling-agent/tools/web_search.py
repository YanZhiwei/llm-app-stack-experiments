"""
网络搜索工具 - 使用 DuckDuckGo 进行免费搜索
"""

from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """使用 DuckDuckGo 进行免费联网搜索"""
    try:
        # 使用 DuckDuckGo 搜索
        with DDGS() as ddgs:
            # 获取前5个搜索结果
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            return f"没有找到关于 '{query}' 的搜索结果"
        
        # 格式化搜索结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', '无标题')
            body = result.get('body', '无描述')
            href = result.get('href', '无链接')
            
            formatted_results.append(
                f"{i}. {title}\n"
                f"   描述: {body[:200]}{'...' if len(body) > 200 else ''}\n"
                f"   链接: {href}\n"
            )
        
        return f"搜索关键词: {query}\n\n" + "\n".join(formatted_results)
        
    except Exception as e:
        return f"搜索失败: {str(e)}。请检查网络连接或稍后重试。" 