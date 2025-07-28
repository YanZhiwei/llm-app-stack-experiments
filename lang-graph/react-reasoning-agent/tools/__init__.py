# 核心工具
from .calculator_tool import calculate_math
from .datetime_tool import (
    add_days_to_date,
    calculate_date_difference,
    get_calendar_info,
    get_current_time,
)
from .search_tool import search_information


def get_react_tools():
    """获取所有ReAct推理工具"""
    return [
        # 核心工具
        search_information,
        calculate_math,
        get_current_time,
        calculate_date_difference,
        get_calendar_info,
        add_days_to_date,
    ]


def get_tool_categories():
    """获取工具分类信息"""
    return {
        "核心工具": [
            "search_information - 搜索信息",
            "calculate_math - 数学计算",
            "get_current_time - 获取当前时间",
            "calculate_date_difference - 计算日期差异",
            "get_calendar_info - 获取日历信息",
            "add_days_to_date - 日期计算"
        ]
    }


def generate_tool_documentation():
    """生成简化的工具文档"""
    tool_categories = get_tool_categories()
    doc = "=== 可用工具列表 ===\n\n"

    for category, tools in tool_categories.items():
        doc += f"📂 {category}:\n"
        for tool in tools:
            doc += f"  🔧 {tool}\n"
        doc += "\n"

    return doc
