"""
Research Agent
基于 Google Gemini Fullstack LangGraph 项目架构
"""

import logging
from typing import Any, Dict

from graph import get_agent_graph
from state import create_initial_state

logger = logging.getLogger(__name__)


def run_research(topic: str) -> Dict[str, Any]:
    """运行研究"""
    logger.info(f"🚀 开始研究: {topic}")

    # 创建初始状态
    initial_state = create_initial_state(topic)

    # 获取图
    graph = get_agent_graph()

    try:
        # 运行图
        final_state = graph.invoke(initial_state)

        logger.info("✅ 研究完成")

        # 返回结果
        return {
            "topic": topic,
            "queries": final_state["search_queries"],
            "results_count": len(final_state["search_results"]),
            "answer": final_state["final_answer"],
            "research_loops": final_state["research_loop_count"],
            "quality_score": final_state["research_quality_score"],
            "is_sufficient": final_state["is_sufficient"]
        }

    except Exception as e:
        logger.error(f"研究失败: {e}")
        return {
            "topic": topic,
            "error": str(e)
        }


def stream_research(topic: str):
    """流式运行研究"""
    logger.info(f"🚀 开始流式研究: {topic}")

    # 创建初始状态
    initial_state = create_initial_state(topic)

    # 获取图
    graph = get_agent_graph()

    try:
        # 流式运行图
        for state in graph.stream(initial_state):
            yield state
    except Exception as e:
        logger.error(f"流式研究失败: {e}")
        yield {"error": str(e)}
