"""
计算器工具 - 执行数学计算
"""

import math

from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """执行数学计算，支持基本运算和数学函数"""
    try:
        # 安全的数学表达式计算
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}。请检查表达式格式，例如: 2+3*4, sqrt(16), sin(pi/2)" 