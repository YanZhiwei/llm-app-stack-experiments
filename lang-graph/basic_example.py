from langgraph.graph import START, StateGraph

# 定义状态类型（可选，简单示例可用dict）
# 这里我们用一个简单的字典作为状态

def hello_node(state: dict):
    print("Hello, LangGraph!")
    # 可以返回新的状态，这里直接返回原状态
    return state

# 创建StateGraph实例，指定状态类型
builder = StateGraph(dict)

# 添加节点
builder.add_node("hello", hello_node)

# 设置起始节点
builder.add_edge(START, "hello")

# 编译为可执行的graph
graph = builder.compile()

# 运行graph
if __name__ == "__main__":
    # 输入可以为空字典
    graph.invoke({}) 