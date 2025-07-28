import asyncio
import os
import sys

from config import config
from langchain_core.messages import HumanMessage
from orchestrator import ReActOrchestrator
from state import ReActState


async def main():
    """ReAct 推理智能体主程序"""

    # 禁用 LangChain 追踪
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""

    # 🎯 ReAct 示例问题集合 - 展示不同复杂度的推理
    # 使用方法：
    # 1. 取消注释下面任意一个问题
    # 2. 注释掉 "获取用户问题" 部分的代码
    # 3. 运行程序测试 ReAct 推理能力
    # 4. 测试完成后恢复原状，使用命令行参数或交互输入

    # 1. 🌟 基础 ReAct 推理 - 数学计算
    # question = "计算圆的面积，半径是5米，然后告诉我这个面积相当于多少个边长为2米的正方形"

    # 2. 📅 时间推理 - 日期计算
    # question = "今天是几号？如果我要在30天后举办一个活动，那天是星期几？距离春节还有多少天？"

    # 3. 🎯 综合推理 - 多工具组合（推荐）
    # question = "帮我规划一个周末活动：查询明天天气，如果天气好就推荐户外活动，如果不好就推荐室内活动，并计算大概需要多少时间"

    # 4. 📚 复杂推理 - 问题分解
    # question = "我需要学习Python编程，帮我制定一个学习计划：查询Python的基础知识，计算学习时间，并告诉我每天应该学习多长时间"

    # 5. 🤖 高级推理 - 多步骤问题
    # question = "我想了解人工智能的发展趋势，查询相关信息，分析当前的技术水平，并预测未来5年的发展方向"

    # 🚀 快速测试模式（取消注释启用）
    # question = "帮我规划一个周末活动：查询明天天气，如果天气好就推荐户外活动，如果不好就推荐室内活动，并计算大概需要多少时间"

    # 获取用户问题
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("🤔 请输入您的问题: ").strip()
        if not question:
            print("❌ 请输入有效的问题")
            return

    print(f"🤔 用户问题: {question}")
    print("🚀 开始 ReAct 推理...")

    # 初始化编排器
    orchestrator = ReActOrchestrator()
    workflow = orchestrator.build_workflow()

    # 初始状态
    initial_state: ReActState = {
        "messages": [HumanMessage(content=question)],
        "current_problem": question,
        "reasoning_steps": [],
        "actions_taken": [],
        "observations": [],
        "thought_process": [],
        "next_action": "",
        "tools_used": [],
        "final_answer": "",
        "reasoning_chain": [],
        "max_iterations": config.DEFAULT_MAX_ITERATIONS,
        "current_iteration": 0,
        "reasoning_strategy": "sequential",
        "problem_complexity": "medium",
        "auto_adjust_iterations": config.AUTO_ADJUST_ITERATIONS,
        "dynamic_iteration_extension": config.DYNAMIC_ITERATION_EXTENSION,
        "recommended_tools": [],
        "success_criteria": "完成问题解答"
    }

    # 执行工作流
    try:
        result = await workflow.ainvoke(initial_state)
        print_results(result)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return


def print_results(result):
    """简洁的结果展示"""
    print("\n" + "="*60)
    print("🎯 ReAct 推理结果")
    print("="*60)

    # 显示推理信息
    current_iter = result.get("current_iteration", 0)
    max_iter = result.get("max_iterations", 5)
    print(f"📊 推理轮次: {current_iter}/{max_iter}")

    # 显示使用的工具
    tools_used = result.get("tools_used", [])
    if tools_used:
        print(f"🔧 使用工具: {', '.join(tools_used)}")

    # 显示最终答案
    final_answer = result.get("final_answer", "")
    if final_answer:
        print(f"\n✅ 最终答案:")
        print(f"{final_answer}")
    else:
        # 从最后一条消息中提取答案
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            content = str(last_message.content)

            # 提取最终答案
            extracted_answer = extract_final_answer(content)
            if extracted_answer:
                print(f"\n✅ 最终答案:")
                print(f"{extracted_answer}")
            else:
                print(f"\n📝 最后响应:")
                print(f"{content}")
        else:
            print("\n❌ 未能获得最终答案")

    print("="*60)


def extract_final_answer(content: str) -> str:
    """从响应中提取最终答案"""
    content_lower = content.lower()
    markers = [
        "final answer:", "最终答案:",
        "answer:", "答案:",
        "result:", "结果:",
        "结论:", "conclusion:"
    ]

    for marker in markers:
        if marker in content_lower:
            start_idx = content_lower.find(marker)
            answer_start = start_idx + len(marker)
            answer = content[answer_start:].strip()
            if answer.startswith('\n'):
                answer = answer[1:]
            return answer

    return ""


if __name__ == "__main__":
    asyncio.run(main())
