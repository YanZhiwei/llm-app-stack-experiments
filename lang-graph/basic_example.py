"""
LangGraph 基础示例 - 简单的多节点工作流

这个示例展示了如何：
1. 定义状态结构（使用TypedDict）
2. 创建多个节点函数
3. 构建图结构并连接节点
4. 执行图并观察状态变化

运行方式：uv run python basic_example.py
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 定义状态结构 - 使用TypedDict确保类型安全
class WorkflowState(TypedDict):
    message: str
    step_count: int
    user_name: str


def greeting_node(state: WorkflowState) -> WorkflowState:
    """问候节点 - 初始化用户信息"""
    print(f"📝 步骤 {state['step_count']}: 开始问候流程")

    return {
        "message": f"你好，{state['user_name']}！欢迎使用 LangGraph！",
        "step_count": state["step_count"] + 1,
        "user_name": state["user_name"]
    }


def processing_node(state: WorkflowState) -> WorkflowState:
    """处理节点 - 模拟一些处理逻辑"""
    print(f"⚙️  步骤 {state['step_count']}: 正在处理请求...")

    return {
        "message": f"{state['message']} 处理完成！",
        "step_count": state["step_count"] + 1,
        "user_name": state["user_name"]
    }


def farewell_node(state: WorkflowState) -> WorkflowState:
    """告别节点 - 结束流程"""
    print(f"👋 步骤 {state['step_count']}: 结束流程")

    return {
        "message": f"{state['message']} 再见，{state['user_name']}！",
        "step_count": state["step_count"] + 1,
        "user_name": state["user_name"]
    }


def create_workflow_graph():
    """创建并配置工作流图"""
    # 创建StateGraph实例，指定状态类型
    builder = StateGraph(WorkflowState)

    # 添加节点
    builder.add_node("greeting", greeting_node)
    builder.add_node("processing", processing_node)
    builder.add_node("farewell", farewell_node)

    # 设置节点连接关系
    builder.add_edge(START, "greeting")
    builder.add_edge("greeting", "processing")
    builder.add_edge("processing", "farewell")
    builder.add_edge("farewell", END)

    # 编译为可执行的graph
    return builder.compile()


def main():
    """主函数 - 演示工作流执行"""
    print("🚀 LangGraph 基础示例启动")
    print("=" * 50)

    # 创建工作流图
    graph = create_workflow_graph()

    # 定义初始状态
    initial_state: WorkflowState = {
        "message": "",
        "step_count": 1,
        "user_name": "开发者"
    }

    # 执行工作流
    print("开始执行工作流...")
    result = graph.invoke(initial_state)

    print("=" * 50)
    print("✅ 工作流执行完成")
    print(f"最终消息: {result['message']}")
    print(f"总步骤数: {result['step_count'] - 1}")


if __name__ == "__main__":
    main()
