import os
import time
from typing import TYPE_CHECKING, Any, Dict, List

from config import config
from langchain_core.messages import AIMessage, HumanMessage

# 新增导入
from langchain_openai import AzureChatOpenAI
from prompts import get_react_system_prompt
from tools import get_react_tools

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续执行
    pass

if TYPE_CHECKING:
    from state import ReActState

# Azure OpenAI 配置
AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# 创建LLM并绑定工具
llm = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,  # type: ignore
        temperature=0.2,
    )
    # 绑定工具到LLM - 这是官方推荐的方式
    tools = get_react_tools()
    llm_with_tools = llm.bind_tools(tools)


async def react_reasoning_agent(state: 'ReActState') -> 'ReActState':
    """标准ReAct推理智能体 - 使用Thought/Action/Observation模式"""

    print(f"\n🧠 [步骤{state.get('current_iteration', 0)}] 开始推理...")

    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", config.DEFAULT_MAX_ITERATIONS)
    current_problem = state.get("current_problem", "")

    # 检查是否达到最大迭代次数
    if current_iter >= max_iter:
        print(f"⚠️ 达到最大迭代次数 {max_iter}，结束推理")
        return {
            **state,
            "next_action": "end"
        }

    # 如果没有配置LLM，直接结束
    if not llm_with_tools:
        print("⚠️ 未配置LLM，无法进行推理")
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content="未配置LLM，无法进行推理")],
            "next_action": "end"
        }

    try:
        # 构建ReAct格式的提示词
        messages = state["messages"]

        # 使用标准的ReAct系统提示词
        system_prompt = get_react_system_prompt()

        # 构建完整的消息列表
        full_messages = [HumanMessage(content=system_prompt)] + messages

        # 使用绑定工具的LLM进行推理
        response = await llm_with_tools.ainvoke(full_messages)

        # 更新状态
        new_state = {
            **state,
            "messages": state["messages"] + [response],
            "current_iteration": current_iter + 1,
        }

        # 检查是否有工具调用
        tool_calls = getattr(response, 'tool_calls', None)
        if tool_calls:
            print(f"🔧 检测到工具调用: {len(tool_calls)} 个")
            new_state["next_action"] = "tools"
        else:
            # 检查是否包含最终答案
            content = str(response.content).lower()
            if "final answer:" in content or "最终答案:" in content:
                print("✅ 推理完成，找到最终答案")
                new_state["next_action"] = "end"
                # 提取最终答案
                final_answer = extract_final_answer(str(response.content))
                if final_answer:
                    new_state["final_answer"] = final_answer
            else:
                print("🔄 继续推理")
                new_state["next_action"] = "reasoning"

        return new_state

    except Exception as e:
        print(f"❌ 推理失败: {e}")
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"推理失败: {str(e)}")],
            "current_iteration": current_iter + 1,
            "next_action": "end"
        }


def extract_final_answer(content: str) -> str:
    """从响应中提取最终答案"""
    content_lower = content.lower()

    # 查找最终答案标记
    markers = [
        "final answer:",
        "最终答案:",
        "answer:",
        "答案:",
        "result:",
        "结果:"
    ]

    for marker in markers:
        if marker in content_lower:
            start_idx = content_lower.find(marker)
            answer_start = start_idx + len(marker)
            answer = content[answer_start:].strip()
            # 清理答案
            if answer.startswith('\n'):
                answer = answer[1:]
            return answer

    # 如果没有找到标记，返回整个内容
    return content


async def react_executor_agent(state: 'ReActState') -> 'ReActState':
    """ReAct执行智能体 - 处理工具执行结果"""

    print(f"\n🔧 [步骤{state.get('current_iteration', 0)}] 处理工具结果...")

    # 获取最后一条消息（工具执行结果）
    last_message = state["messages"][-1]
    tool_output = str(last_message.content)

    print(
        f"📋 工具执行结果: {tool_output[:200]}{'...' if len(tool_output) > 200 else ''}")

    # 检查是否达到最大迭代次数
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", config.DEFAULT_MAX_ITERATIONS)

    if current_iter >= max_iter:
        print(f"⚠️ 达到最大迭代次数 {max_iter}，结束推理")
        return {
            **state,
            "next_action": "end"
        }

    # 继续推理
    return {
        **state,
        "next_action": "reasoning"
    }
