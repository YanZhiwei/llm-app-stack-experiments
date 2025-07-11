from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agents import react_reasoning_agent, react_executor_agent
from state import ReActState
from tools import get_react_tools


def should_continue(state: ReActState) -> str:
    """决定ReAct推理是否继续"""
    next_action = state.get("next_action", "")
    
    # 如果明确指示结束
    if next_action == "end":
        return "end"
    
    # 检查最后一条消息是否有工具调用
    messages = state["messages"]
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
    
    # 检查是否需要继续推理
    if next_action == "continue_reasoning":
        return "reasoning"
    
    # 检查迭代次数
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", 5)
    
    if current_iter >= max_iter:
        return "end"
    
    # 默认继续推理
    return "reasoning"


def should_continue_after_tools(state: ReActState) -> str:
    """工具执行后的决策函数"""
    next_action = state.get("next_action", "")
    
    if next_action == "end":
        return "end"
    
    # 检查是否达到最大迭代次数
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", 5)
    
    if current_iter >= max_iter:
        return "end"
    
    # 默认到执行器处理工具结果
    return "executor"


class ReActOrchestrator:
    """ReAct推理系统编排器"""
    
    def __init__(self):
        self.tools = get_react_tools()
        self.tool_node = ToolNode(self.tools)

    def build_workflow(self) -> StateGraph:
        """构建ReAct推理工作流"""
        workflow = StateGraph(ReActState)
        
        # 添加节点
        workflow.add_node("reasoning", react_reasoning_agent)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("executor", react_executor_agent)
        
        # 设置入口点
        workflow.set_entry_point("reasoning")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "reasoning",
            should_continue,
            {
                "tools": "tools",
                "reasoning": "reasoning",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "tools",
            should_continue_after_tools,
            {
                "executor": "executor",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "executor",
            should_continue,
            {
                "reasoning": "reasoning",
                "end": END
            }
        )
        
        return workflow.compile() 