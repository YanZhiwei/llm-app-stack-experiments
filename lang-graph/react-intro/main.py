import asyncio

from langchain_core.messages import HumanMessage

from orchestrator import ReActOrchestrator
from state import ReActState


async def main():
    """ReAct推理系统主函数"""
    
    print("🧠 ReAct推理系统启动！")
    print("=" * 50)
    print("ReAct (Reasoning and Acting) 是一种大模型推理方法")
    print("通过思考(Think) -> 行动(Act) -> 观察(Observe)的循环来解决问题")
    print("=" * 50)
    
    # 创建编排器
    orchestrator = ReActOrchestrator()
    workflow = orchestrator.build_workflow()
    
    # 可以尝试的示例问题
    example_problems = [
        "请帮我计算 15 + 27 * 3 的结果",
        "什么是LangGraph？它有什么特点？",
        "比较Python和Java的优缺点",
        "解释一下ReAct推理方法的工作原理",
        "北京今天的天气怎么样？"
    ]
    
    print("\n💡 示例问题:")
    for i, problem in enumerate(example_problems, 1):
        print(f"{i}. {problem}")
    
    print("\n🔧 可用工具:")
    print("- search_information: 搜索相关信息")
    print("- calculate_math: 数学计算") 
    print("- analyze_problem: 问题分析")
    print("- store_memory: 存储信息")
    print("- retrieve_memory: 检索信息")
    print("- verify_answer: 验证答案")
    
    # 默认问题（可以修改这里来测试不同问题）
    user_question = "请帮我计算 (5 + 3) * 2 - 1 的结果，并解释计算过程"
    
    print(f"\n🤔 处理问题: {user_question}")
    print("-" * 50)
    
    # 构建初始状态
    initial_state: ReActState = {
        "messages": [
            HumanMessage(content=user_question)
        ],
        "current_problem": user_question,
        "reasoning_steps": [],
        "actions_taken": [],
        "observations": [],
        "thought_process": [],
        "next_action": "",
        "tools_used": [],
        "final_answer": "",
        "reasoning_chain": [],
        "max_iterations": 5,
        "current_iteration": 0
    }
    
    try:
        # 执行推理工作流
        result = await workflow.ainvoke(initial_state)
        
        # 显示结果
        print("\n" + "=" * 50)
        print("📊 推理过程总结")
        print("=" * 50)
        
        print(f"\n📝 问题: {result.get('current_problem', '')}")
        print(f"🔄 推理轮次: {result.get('current_iteration', 0)}/{result.get('max_iterations', 5)}")
        
        # 显示推理链
        reasoning_chain = result.get("reasoning_chain", [])
        if reasoning_chain:
            print(f"\n🧠 推理链:")
            for i, step in enumerate(reasoning_chain, 1):
                print(f"\n第{i}轮:")
                print(f"  🤔 思考: {step.get('thought', '')}")
                print(f"  🔧 行动: {step.get('action', '')}")
                print(f"  👁️ 观察: {step.get('observation', '')}")
        
        # 显示思考过程
        thought_process = result.get("thought_process", [])
        if thought_process:
            print(f"\n💭 思考过程:")
            for i, thought in enumerate(thought_process, 1):
                print(f"  {i}. {thought}")
        
        # 显示使用的工具
        tools_used = result.get("tools_used", [])
        if tools_used:
            print(f"\n🛠️ 使用的工具: {', '.join(set(tools_used))}")
        
        # 显示最终答案
        final_answer = result.get("final_answer", "")
        if final_answer:
            print(f"\n✅ 最终答案:")
            print(f"{final_answer}")
        
        # 显示所有消息（可选，用于调试）
        print(f"\n📨 完整对话历史:")
        for i, msg in enumerate(result.get("messages", []), 1):
            msg_type = "🙋 用户" if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls') else "🤖 助手"
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg_type += " (工具调用)"
            print(f"  {i}. {msg_type}: {msg.content}")
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def demo_different_problems():
    """演示不同类型问题的处理"""
    problems = [
        "计算 sqrt(144) + 5^2",
        "什么是机器学习？",
        "比较LangChain和LangGraph的区别",
    ]
    
    for problem in problems:
        print(f"\n{'='*60}")
        print(f"问题: {problem}")
        print('='*60)
        
        # 这里可以运行每个问题的推理过程
        # 为了简化，只显示问题
        

if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
    
    # 如果想要演示多个问题，可以取消注释下面的行
    # demo_different_problems() 