import operator
from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.messages import BaseMessage


class SuperAgentState(TypedDict):
    """Super Agent状态定义"""
    messages: Annotated[List[BaseMessage], operator.add]
    current_task: str
    task_plan: List[str]
    collected_data: Dict[str, Any]
    reasoning_log: List[str]
    next_action: str
    tools_used: List[str]
    final_result: str 