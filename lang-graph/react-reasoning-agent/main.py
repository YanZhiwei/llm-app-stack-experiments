import asyncio
import os

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from config import config
from orchestrator import ReActOrchestrator
from state import ReActState


async def main():

    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""

    # 🎯 演示问题集合 - 展示不同功能
    # 选择一个问题取消注释，其他保持注释状态

    # 1. 🌤️ 天气查询 + 文本分析 (在线API + 文本处理)
    # demo_question = '''
    # 查询今天上海的天气情况，分析天气描述文本，并判断是否适合户外运动
    '''

    # # 2. 🧮 数学计算 + 单位转换 (计算工具 + 单位转换)
    # demo_question = '''
    # 计算一个半径为5米的圆形花园的面积，然后将结果转换为平方英尺
    # '''

    # # 3. 📅 日期时间 + 日历分析 (日期时间工具)
    # demo_question = '''
    # 今天是几号？计算距离2024年春节还有多少天，并显示下个月的日历
    # '''

    # # 4. ✈️ 航班查询 + 机场信息 (航班工具)
    # demo_question = '''
    # 查询明天从上海到北京的航班信息，并提供浦东机场的详细信息
    # '''

    # # 5. 🎲 随机生成 + 密码安全 (随机生成工具)
    # demo_question = '''
    # 生成一个16位的强密码，包含特殊字符，并分析其安全强度
    # '''

    # # 6. 📝 Markdown报告 + 图表生成 (Markdown工具)
    # demo_question = '''
    # 创建一个关于人工智能发展趋势的专业报告，包含表格和ASCII图表
    # '''

    # # 7. 🔍 文本处理 + 模式提取 (文本处理工具)
    # demo_question = '''
    # 分析这段文本："联系我们：张三 13812345678，邮箱：zhangsan@example.com，网站：https://www.example.com"，提取其中的电话、邮箱和网址
    # '''

    # # 8. 🌐 综合查询 + 汇率转换 (在线API工具)
    # demo_question = '''
    # 查询美元兑人民币的汇率，为网址"https://www.openai.com"生成二维码，并获取一个励志名言
    # '''

    # # 9. 🧠 复杂推理 + 多工具组合 (综合任务)
    demo_question = '''
  帮我规划一个周末的上海一日游：查询明天天气，推荐适合的景点，计算大概费用，并生成一个详细的出行计划Markdown报告
    '''

    # # 10. 📊 数据分析 + 日志统计 (日志分析工具)
    # demo_question = '''
    # 我需要规划一个AI 销售 Agent项目，帮我分析步骤并生成并保存Markdown报告
    # '''

    print(f"🤔 用户问题: {demo_question}")
    print("🚀 开始推理...")

    orchestrator = ReActOrchestrator()
    workflow = orchestrator.build_workflow()

    # 简化的初始状态
    initial_state: ReActState = {
        "messages": [HumanMessage(content=demo_question)],
        "current_problem": demo_question,
        "reasoning_steps": [],
        "actions_taken": [],
        "observations": [],
        "thought_process": [],
        "next_action": "",
        "tools_used": [],
        "final_answer": "",
        "reasoning_chain": [],
        "max_iterations": config.DEFAULT_MAX_ITERATIONS,
        "dynamic_iteration_extension": config.DYNAMIC_ITERATION_EXTENSION,  # 是否允许动态扩展迭代次数
        "current_iteration": 0,
        "reasoning_strategy": "sequential",  # 默认策略
        "problem_complexity": "medium",  # 默认复杂度
        "auto_adjust_iterations": config.AUTO_ADJUST_ITERATIONS,  # 🆕 使用配置文件中的设置
        "recommended_tools": [],  # LLM推荐的工具
        "success_criteria": "完成问题解答"  # 成功标准
    }

    # 🆕 显示当前配置信息
    print(f"📋 当前配置:")
    print(
        f"   - 迭代控制模式: {getattr(config, 'ITERATION_CONTROL_MODE', 'intelligent')}")
    print(f"   - 自动调整迭代次数: {config.AUTO_ADJUST_ITERATIONS}")
    print(f"   - 动态扩展: {config.DYNAMIC_ITERATION_EXTENSION}")
    if hasattr(config, 'INTELLIGENT_ADJUSTMENT_CONFIG'):
        intelligent_config = config.INTELLIGENT_ADJUSTMENT_CONFIG
        print(f"   - 智能调整基础轮次: {intelligent_config.get('base_iterations', 6)}")
        print(
            f"   - 安全上限: {intelligent_config.get('max_safe_iterations', 20)}")
    print()

    # 执行工作流
    # 🆕 设置合理的递归限制配置
    # 考虑到每个推理轮次包含 reasoning -> tools -> executor 三个步骤
    # 最大迭代次数 * 3 + 一些缓冲，但不超过合理范围
    max_recursion_limit = min(config.MAX_DYNAMIC_ITERATIONS * 3 + 10, 50)

    # 配置工作流执行参数
    workflow_config = RunnableConfig(
        recursion_limit=max_recursion_limit,
        configurable={}
    )

    print(f"🔧 工作流配置: 递归限制={max_recursion_limit}")

    try:
        # type: ignore
        result = await workflow.ainvoke(initial_state, config=workflow_config)
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        # 如果递归限制配置失败，使用默认配置
        print("🔄 使用默认配置重试...")
        result = await workflow.ainvoke(initial_state)  # type: ignore

    # 简化的结果展示
    print_results(result)


def print_results(result):
    """简洁的结果展示"""
    print("\n" + "="*50)
    print("🎯 推理结果")
    print("="*50)

    # 显示轮次信息
    current_iter = result.get("current_iteration", 0)
    max_iter = result.get("max_iterations", 5)
    print(f"📊 推理轮次: {current_iter}/{max_iter}")

    # 显示策略信息
    strategy = result.get("reasoning_strategy", "未知")
    complexity = result.get("problem_complexity", "未知")
    print(f"🧭 策略: {strategy} | 复杂度: {complexity}")

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
        print("\n❌ 未能获得最终答案")

    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
