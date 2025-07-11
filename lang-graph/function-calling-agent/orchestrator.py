from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agents import executor_agent, planner_agent
from state import SuperAgentState
from tools import get_tools


def should_continue(state: SuperAgentState) -> str:
    """决定是否继续执行工具"""
    messages = state["messages"]
    last_message = messages[-1]
    # 如果最后一条消息是 AIMessage 且有 tool_calls，则执行工具
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return "end"


class SuperAgentOrchestrator:
    def __init__(self):
        self.tools = get_tools()
        self.tool_node = ToolNode(self.tools)
        self.reasoning_log = []

    def build_workflow(self) -> StateGraph:
        workflow = StateGraph(SuperAgentState)
        workflow.add_node("planner", planner_agent)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("executor", executor_agent)
        
        workflow.set_entry_point("planner")
        workflow.add_conditional_edges(
            "planner",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "executor")
        workflow.add_edge("executor", END)
        return workflow.compile() 