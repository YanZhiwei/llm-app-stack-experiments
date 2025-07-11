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
    reasoning_chain: List[Dict[str, str]]  # 推理链 [{"thought": "", "action": "", "observation": ""}]
    max_iterations: int  # 最大迭代次数
    current_iteration: int  # 当前迭代次数 