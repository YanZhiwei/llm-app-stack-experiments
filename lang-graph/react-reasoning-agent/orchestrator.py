import time

from config import config
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from state import ReActState
from tools import get_react_tools

from agents import react_executor_agent, react_reasoning_agent


def should_continue(state: ReActState) -> str:
    """简化的决策函数 - 使用bind_tools方式"""
    next_action = state.get("next_action", "")

    # 如果明确指示结束
    if next_action == "end":
        return "end"

    # 检查是否有工具调用
    messages = state["messages"]
    if messages:
        last_message = messages[-1]
        tool_calls = getattr(last_message, 'tool_calls', None)
        if tool_calls:
            return "tools"

    # 检查迭代次数
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", config.DEFAULT_MAX_ITERATIONS)

    if current_iter >= max_iter:
        return "end"

    # 默认继续推理
    return "reasoning"


class ReActOrchestrator:
    """简化的ReAct推理系统编排器 - 使用bind_tools方式"""

    def __init__(self):
        self.tools = get_react_tools()
        # 使用LangGraph的ToolNode，自动处理工具调用
        self.tool_node = ToolNode(self.tools)

    def build_workflow(self):
        """构建简化的ReAct推理工作流"""
        workflow = StateGraph(ReActState)

        # 添加节点 - 利用LangGraph内置功能
        workflow.add_node("reasoning", react_reasoning_agent)
        workflow.add_node("tools", self.tool_node)  # ToolNode自动处理工具调用
        workflow.add_node("executor", react_executor_agent)

        # 设置入口点
        workflow.set_entry_point("reasoning")

        # 简化的条件边 - 让LangGraph自动处理工具调用
        workflow.add_conditional_edges(
            "reasoning",
            should_continue,
            {
                "tools": "tools",
                "reasoning": "reasoning",
                "end": END
            }
        )

        # 工具执行后直接到执行器
        workflow.add_edge("tools", "executor")

        # 执行器后继续推理或结束
        workflow.add_conditional_edges(
            "executor",
            should_continue,
            {
                "reasoning": "reasoning",
                "end": END
            }
        )

        return workflow.compile()
