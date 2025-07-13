"""
Research Agent - 研究智能体
基于 Google Gemini Fullstack LangGraph 项目架构
"""

__version__ = "0.2.0"
__author__ = "Research Agent Team"
__description__ = "研究智能体系统 - 基于LangGraph和Azure OpenAI的Research Agent"

from .agent import run_research, stream_research
from .config import Config, config
from .graph import create_agent_graph, get_agent_graph
from .state import AgentState, create_initial_state

__all__ = [
    "run_research",
    "stream_research",
    "Config",
    "config",
    "create_agent_graph",
    "get_agent_graph",
    "AgentState",
    "create_initial_state"
]
