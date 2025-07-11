from .search_tool import search_information
from .calculator_tool import calculate_math
from .reasoning_tool import analyze_problem
from .memory_tool import store_memory, retrieve_memory
from .verification_tool import verify_answer

def get_react_tools():
    """获取所有ReAct推理工具"""
    return [
        search_information,
        calculate_math,
        analyze_problem,
        store_memory,
        retrieve_memory,
        verify_answer,
    ] 