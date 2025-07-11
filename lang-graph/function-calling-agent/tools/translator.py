"""
翻译工具 - 使用免费翻译服务
"""

from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def translate_text(text: str, target_language: str = "en") -> str:
    """使用免费翻译服务翻译文本"""
    try:
        # 使用 DuckDuckGo 的翻译功能
        with DDGS() as ddgs:
            result = ddgs.translate(text, to=target_language)
            if result:
                return f"翻译结果 ({target_language}): {result}"
            else:
                return "翻译失败，请检查输入文本和目标语言代码"
    except Exception as e:
        return f"翻译失败: {str(e)}。支持的语言代码如: en(英语), zh(中文), ja(日语), ko(韩语), fr(法语), de(德语), es(西班牙语)" 