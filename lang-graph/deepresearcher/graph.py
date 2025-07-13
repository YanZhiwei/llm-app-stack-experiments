"""
Agent图构建
"""

import logging

from langgraph.graph import END, StateGraph

from nodes import (
    generate_answer,
    generate_queries,
    reflection,
    should_continue_research,
    web_research,
)
from state import AgentState

logger = logging.getLogger(__name__)


def create_agent_graph():
    """创建Agent图"""
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("web_research", web_research)
    workflow.add_node("reflection", reflection)
    workflow.add_node("generate_answer", generate_answer)

    # 设置入口点
    workflow.set_entry_point("generate_queries")

    # 添加边
    workflow.add_edge("generate_queries", "web_research")
    workflow.add_edge("web_research", "reflection")

    # 添加条件边：从reflection到决策点
    workflow.add_conditional_edges(
        "reflection",
        should_continue_research,
        {
            "generate_queries": "web_research",  # 继续研究
            "generate_answer": "generate_answer"  # 生成最终答案
        }
    )

    workflow.add_edge("generate_answer", END)

    return workflow.compile()


# 全局图实例
_agent_graph = None


def get_agent_graph():
    """获取全局Agent图实例"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
    return _agent_graph
