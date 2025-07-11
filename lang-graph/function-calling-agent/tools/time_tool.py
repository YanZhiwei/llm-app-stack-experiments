"""
时间工具 - 获取当前时间和日期
"""

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前时间和日期"""
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S %A')}" 