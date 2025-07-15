from graph import AgentState, build_graph

if __name__ == "__main__":
    print("=== Plan-and-Execute 智能体 (langgraph 版) ===")
    goal = input("请输入你的目标: ")
    g = build_graph()
    state = AgentState(goal=goal)
    final_state = g.invoke(state)
    print("\n【详细计划】")
    for s in final_state["plan"]:
        print("  ", s)
    print("\n【执行建议】")
    for r in final_state["results"]:
        print("  ", r)
    print("\n【历史记录】")
    for h in final_state["history"]:
        print("  ", h)
