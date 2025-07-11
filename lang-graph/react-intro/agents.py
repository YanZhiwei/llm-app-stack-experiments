import os
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage

# 新增导入
from langchain_openai import AzureChatOpenAI

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续执行
    pass

if TYPE_CHECKING:
    from state import ReActState

# Azure OpenAI 配置（按照记忆，使用gpt-4o-mini）
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

llm = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        openai_api_key=AZURE_OPENAI_API_KEY,
        temperature=0.2,
    )

async def react_reasoning_agent(state: 'ReActState') -> 'ReActState':
    """ReAct推理Agent：实现思考-行动-观察的循环"""
    
    # 获取用户的问题
    user_message = ""
    for msg in state["messages"]:
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            user_message = msg.content
            break
    
    # 检查是否达到最大迭代次数
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", 5)
    
    if current_iter >= max_iter:
        # 达到最大迭代次数，结束推理
        ai_message = AIMessage(
            content=f"已达到最大推理轮次({max_iter})，结束思考过程。\n\n基于已有信息，我的最终答案是:\n{state.get('final_answer', '抱歉，无法在限定轮次内完全解决这个问题。')}"
        )
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "next_action": "end"
        }
    
    # 构建当前的推理上下文
    context = f"问题: {user_message}\n\n"
    
    # 添加之前的推理链
    if state.get("reasoning_chain"):
        context += "之前的推理过程:\n"
        for i, step in enumerate(state["reasoning_chain"], 1):
            context += f"第{i}轮:\n"
            context += f"思考: {step.get('thought', '')}\n"
            context += f"行动: {step.get('action', '')}\n"
            context += f"观察: {step.get('observation', '')}\n\n"
    
    # 如果配置了LLM，使用智能推理
    if llm:
        try:
            prompt = f"""{context}

当前是第{current_iter + 1}轮推理。

可用工具:
1. search_information(query) - 搜索相关信息
2. calculate_math(expression) - 数学计算
3. analyze_problem(problem) - 分析问题
4. store_memory(key, value) - 存储信息
5. retrieve_memory(key) - 检索信息
6. verify_answer(answer, problem) - 验证答案

请按照ReAct方法进行推理，返回JSON格式:
{{
    "thought": "你的思考过程",
    "action": "要执行的行动类型", 
    "tool_name": "具体工具名称",
    "tool_args": {{"参数名": "参数值"}},
    "need_more_info": true/false
}}

如果你已经有足够信息可以给出最终答案，请设置need_more_info为false，并在thought中包含最终答案。
只返回JSON，不要其他内容。"""

            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            # 解析LLM响应
            import json
            try:
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                reasoning = json.loads(content.strip())
                thought = reasoning.get("thought", "进行思考...")
                action = reasoning.get("action", "搜索信息")
                tool_name = reasoning.get("tool_name", "search_information")
                tool_args = reasoning.get("tool_args", {"query": user_message})
                need_more_info = reasoning.get("need_more_info", True)
                
                # 检查是否完成推理
                if not need_more_info:
                    # 提取最终答案
                    final_answer = thought
                    
                    ai_message = AIMessage(
                        content=f"思考完成！\n\n思路: {thought}\n\n最终答案: {final_answer}"
                    )
                    
                    return {
                        **state,
                        "messages": state["messages"] + [ai_message],
                        "final_answer": final_answer,
                        "thought_process": state["thought_process"] + [thought],
                        "next_action": "end"
                    }
                
            except (json.JSONDecodeError, KeyError) as e:
                # JSON解析失败，使用回退逻辑
                thought = "LLM响应解析失败，使用启发式推理"
                tool_name = "analyze_problem"
                tool_args = {"problem": user_message}
                
        except Exception as e:
            # LLM调用失败，使用回退逻辑
            thought = f"LLM调用失败: {e}，使用启发式推理"
            tool_name = "analyze_problem"
            tool_args = {"problem": user_message}
            
    else:
        # 回退方案：使用启发式规则推理
        if current_iter == 0:
            # 第一轮：分析问题
            thought = "开始分析问题，确定问题类型和解决策略"
            tool_name = "analyze_problem"
            tool_args = {"problem": user_message}
        elif "数学" in user_message.lower() or any(op in user_message for op in ['+', '-', '*', '/', '=']):
            # 数学问题
            thought = "这是一个数学问题，需要进行计算"
            tool_name = "calculate_math"
            # 尝试提取数学表达式
            import re
            math_expr = re.search(r'[\d+\-*/().\s]+', user_message)
            expression = math_expr.group().strip() if math_expr else "2+2"
            tool_args = {"expression": expression}
        else:
            # 默认搜索
            thought = "需要搜索相关信息来回答这个问题"
            tool_name = "search_information"
            tool_args = {"query": user_message}
    
    # 创建工具调用
    tool_call = {
        "name": tool_name,
        "args": tool_args,
        "id": f"call_react_{current_iter + 1}"
    }
    
    ai_message = AIMessage(
        content=f"第{current_iter + 1}轮推理:\n\n🤔 思考: {thought}\n\n🔧 行动: 使用 {tool_name} 工具",
        tool_calls=[tool_call]
    )
    
    # 更新推理链
    reasoning_chain = state.get("reasoning_chain", [])
    reasoning_chain.append({
        "thought": thought,
        "action": f"使用 {tool_name} 工具",
        "observation": "等待工具执行结果..."
    })
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "thought_process": state["thought_process"] + [thought],
        "reasoning_chain": reasoning_chain,
        "current_iteration": current_iter + 1,
        "next_action": "execute_tools"
    }

async def react_executor_agent(state: 'ReActState') -> 'ReActState':
    """ReAct执行Agent：处理工具调用结果并决定下一步"""
    
    # 获取最后一条消息（工具执行结果）
    last_message = state["messages"][-1]
    tool_output = last_message.content
    
    # 更新推理链中的观察结果
    reasoning_chain = state.get("reasoning_chain", [])
    if reasoning_chain:
        reasoning_chain[-1]["observation"] = tool_output
    
    # 分析工具输出，决定是否需要继续推理
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", 5)
    
    # 检查是否找到了满意的答案
    confidence_indicators = [
        "结果:", "答案:", "计算表达式:", "找到相关信息:", 
        "成功存储", "验证评分", "问题分析"
    ]
    
    has_useful_result = any(indicator in tool_output for indicator in confidence_indicators)
    
    # 检查是否需要更多信息
    need_more_indicators = [
        "未找到", "错误", "失败", "无法", "不确定", "需要更多", "建议进一步"
    ]
    
    needs_more_info = any(indicator in tool_output for indicator in need_more_indicators)
    
    if has_useful_result and not needs_more_info and current_iter >= 2:
        # 有了有用的结果，且迭代次数足够，可以结束
        final_answer = f"基于推理过程，我的答案是:\n{tool_output}"
        
        ai_message = AIMessage(
            content=f"✅ 推理完成！\n\n观察: {tool_output}\n\n{final_answer}"
        )
        
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "final_answer": final_answer,
            "observations": state["observations"] + [tool_output],
            "reasoning_chain": reasoning_chain,
            "next_action": "end"
        }
    
    elif current_iter >= max_iter:
        # 达到最大迭代次数
        final_answer = f"经过{max_iter}轮推理，基于收集到的信息:\n{tool_output}"
        
        ai_message = AIMessage(
            content=f"⏰ 达到最大推理轮次。\n\n观察: {tool_output}\n\n{final_answer}"
        )
        
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "final_answer": final_answer,
            "observations": state["observations"] + [tool_output],
            "reasoning_chain": reasoning_chain,
            "next_action": "end"
        }
    
    else:
        # 需要继续推理
        ai_message = AIMessage(
            content=f"📝 观察: {tool_output}\n\n继续推理..."
        )
        
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "observations": state["observations"] + [tool_output],
            "reasoning_chain": reasoning_chain,
            "next_action": "continue_reasoning"
        } 