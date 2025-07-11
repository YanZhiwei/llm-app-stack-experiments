import asyncio

from langchain_core.messages import HumanMessage

from orchestrator import SuperAgentOrchestrator
from state import SuperAgentState


async def main():
    orchestrator = SuperAgentOrchestrator()
    workflow = orchestrator.build_workflow()
    # 示例初始状态
    state: SuperAgentState = {
        "messages": [
            HumanMessage(content="请帮我查询北京今天的天气情况")
        ],
        "current_task": "查询北京天气",
        "task_plan": [],
        "collected_data": {},
        "reasoning_log": [],
        "next_action": "",
        "tools_used": [],
        "final_result": ""
    }
    result = await workflow.ainvoke(state)

    print("\n==== 推理日志 ====")
    for log in result.get("reasoning_log", []):
        print(log)

    print("\n==== 消息历史 ====")
    for msg in result.get("messages", []):
        print(msg)

    print("\n==== 工具调用 ====")
    for tool in result.get("tools_used", []):
        print(tool)

    print("\n==== 最终结果 ====")
    print(result.get("final_result", ""))

if __name__ == "__main__":
    asyncio.run(main())
