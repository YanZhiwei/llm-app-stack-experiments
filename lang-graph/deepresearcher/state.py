"""
Agent状态定义
"""

from typing import Any, List

from langchain_core.messages import HumanMessage
from pydantic import BaseModel


class AgentState(BaseModel):
    """Agent状态"""
    messages: List[Any] = []
    research_topic: str = ""
    search_queries: List[str] = []
    search_results: List[dict] = []
    final_answer: str = ""

    # Reflection相关字段
    research_loop_count: int = 0  # 研究循环次数
    max_research_loops: int = 3   # 最大研究循环数
    is_sufficient: bool = False   # 信息是否充分
    knowledge_gap: str = ""       # 知识缺口描述
    follow_up_queries: List[str] = []  # 后续查询
    research_quality_score: float = 0.0  # 研究质量评分


def create_initial_state(topic: str) -> AgentState:
    """创建初始状态"""
    return AgentState(
        messages=[HumanMessage(content=topic)],
        research_topic=topic
    )
