import math
import re
from langchain_core.tools import tool

@tool  
def calculate_math(expression: str) -> str:
    """执行数学计算
    
    Args:
        expression: 数学表达式，支持基本运算和数学函数
    
    Returns:
        计算结果
    """
    
    try:
        # 清理表达式，移除多余空格
        expression = expression.strip()
        
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
        
        return f"计算表达式: {expression}\n结果: {result}"
        
    except ZeroDivisionError:
        return f"计算表达式: {expression}\n错误: 除数不能为零"
        
    except ValueError as e:
        return f"计算表达式: {expression}\n错误: 数值错误 - {str(e)}"
        
    except SyntaxError:
        return f"计算表达式: {expression}\n错误: 语法错误，请检查表达式格式"
        
    except Exception as e:
        return f"计算表达式: {expression}\n错误: {str(e)}" 