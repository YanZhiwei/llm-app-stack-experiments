import operator
from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.messages import BaseMessage


class ReActState(TypedDict):
    """ReAct推理智能体状态定义"""
    messages: Annotated[List[BaseMessage], operator.add]
    current_problem: str  # 当前要解决的问题
    reasoning_steps: List[str]  # 推理步骤
    actions_taken: List[Dict[str, Any]]  # 已执行的动作
    observations: List[str]  # 观察结果
    thought_process: List[str]  # 思考过程
    next_action: str  # 下一步动作
    tools_used: List[str]  # 已使用工具
    final_answer: str  # 最终答案
    # 推理链 [{"thought": "", "action": "", "observation": ""}]
    reasoning_chain: List[Dict[str, str]]
    max_iterations: int  # 最大迭代次数
    current_iteration: int  # 当前迭代次数
    reasoning_strategy: str  # 推理策略
    problem_complexity: str  # 问题复杂度
    auto_adjust_iterations: bool  # 是否自动根据策略调整迭代次数
    dynamic_iteration_extension: bool  # 是否允许动态扩展迭代次数
    recommended_tools: List[str]  # LLM推荐的工具
    success_criteria: str  # 成功标准
