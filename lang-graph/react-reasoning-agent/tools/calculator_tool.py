import math
import re
from typing import Any, Dict, Optional

from langchain_core.tools import tool




@tool
def calculate_math(expression: str, precision: Optional[int] = 2) -> Dict[str, Any]:
    """执行数学计算

    Args:
        expression: 数学表达式，支持基本运算和数学函数
        precision: 保留小数位数，可选，默认2位

    Returns:
        包含计算结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "expression": str,
            "result": float,
            "formatted_result": str
        }
    """

    try:
        # 清理表达式，移除多余空格
        expression = expression.strip()
        precision = precision or 2

        # 安全的数学函数映射
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }

        # 替换一些常见的数学表达式
        expression = expression.replace("^", "**")  # 幂运算
        expression = expression.replace("×", "*")   # 乘法
        expression = expression.replace("÷", "/")   # 除法

        # 处理一些常见的数学函数名称
        expression = re.sub(r'\bsqrt\(([^)]+)\)', r'sqrt(\1)', expression)
        expression = re.sub(r'\bsin\(([^)]+)\)', r'sin(\1)', expression)
        expression = re.sub(r'\bcos\(([^)]+)\)', r'cos(\1)', expression)
        expression = re.sub(r'\btan\(([^)]+)\)', r'tan(\1)', expression)
        expression = re.sub(r'\blog\(([^)]+)\)', r'log(\1)', expression)

        # 执行计算
        result = eval(expression, safe_dict)

        # 格式化结果
        if isinstance(result, (int, float)):
            if precision == 0:
                formatted_result = str(int(result))
            else:
                formatted_result = f"{result:.{precision}f}"
        else:
            formatted_result = str(result)

        return {
            "status": "success",
            "message": "计算成功",
            "expression": expression,
            "result": float(result),
            "formatted_result": formatted_result
        }

    except ZeroDivisionError:
        return {
            "status": "error",
            "message": "除数不能为零",
            "expression": expression,
            "result": 0.0,
            "formatted_result": "错误"
        }

    except ValueError as e:
        return {
            "status": "error",
            "message": f"数值错误: {str(e)}",
            "expression": expression,
            "result": 0.0,
            "formatted_result": "错误"
        }

    except SyntaxError:
        return {
            "status": "error",
            "message": "语法错误，请检查表达式格式",
            "expression": expression,
            "result": 0.0,
            "formatted_result": "错误"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"计算失败: {str(e)}",
            "expression": expression,
            "result": 0.0,
            "formatted_result": "错误"
        }
