import os
import time
from typing import TYPE_CHECKING, Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage

# 新增导入
from langchain_openai import AzureChatOpenAI

from config import config
from reasoning_strategies import (
    ComplexityAnalysisResult,
    ProblemComplexity,
    ReasoningContext,
    ReasoningStrategy,
    strategy_manager,
)
from tools import get_react_tools, resolve_params, resolve_tool_name
from tools.mcp_adapter import mcp_adapter

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

llm = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,  # type: ignore
        temperature=0.2,
    )


async def evaluate_result_quality(
    original_problem: str,
    final_answer: str,
    reasoning_chain: List[Dict[str, str]],
    file_check_result: Dict[str, Any],
    llm
) -> str:
    """评估结果质量并提供优化建议"""

    if not llm:
        return "📊 结果质量评估: 未配置LLM，无法进行评估"

    try:
        # 构建评估上下文
        context = f"""
原始问题: {original_problem}

最终答案: {final_answer}

推理过程概要:
"""

        for i, step in enumerate(reasoning_chain, 1):
            context += f"步骤{i}: {step.get('action', '')}\n"

        context += f"""
文件生成情况:
- 有文件要求: {file_check_result.get('has_file_requirement', False)}
- 生成的文件: {file_check_result.get('existing_files', [])}
- 缺失的文件: {file_check_result.get('missing_files', [])}
"""

        prompt = f"""
请对以下问题解决过程进行质量评估和优化建议：

{context}

请从以下维度进行评估：

**🔍 完整性评估 (0-10分)**
- 是否完全回答了用户的问题？
- 是否遗漏了任何重要信息？
- 是否满足了所有明确提出的要求？

**🎯 准确性评估 (0-10分)**
- 信息是否准确可信？
- 计算和数据是否正确？
- 是否有逻辑错误？

**📋 实用性评估 (0-10分)**
- 结果是否对用户有实际帮助？
- 是否提供了可行的方案？
- 格式是否符合用户期望？

**🎨 呈现质量评估 (0-10分)**
- 答案是否清晰易懂？
- 结构是否合理？
- 是否有足够的细节？

**💡 优化建议**
- 有哪些可以改进的地方？
- 是否需要补充额外信息？
- 有什么后续行动建议？

请用以下格式返回评估结果：

📊 **结果质量评估报告**

🔍 **完整性**: X/10 - 评估说明
🎯 **准确性**: X/10 - 评估说明  
📋 **实用性**: X/10 - 评估说明
🎨 **呈现质量**: X/10 - 评估说明

⭐ **综合评分**: X/10

💡 **优化建议**:
1. 建议1
2. 建议2
3. 建议3

🚀 **后续行动**:
- 行动1
- 行动2
"""

        print("🤖 正在进行结果质量评估...")
        response = await llm.ainvoke([HumanMessage(content=prompt)])

        assessment = str(response.content).strip()
        print("📊 质量评估完成")

        return assessment

    except Exception as e:
        print(f"❌ 结果质量评估失败: {e}")
        return f"📊 结果质量评估: 评估过程中出现错误 - {str(e)}"


async def react_reasoning_agent(state: 'ReActState') -> 'ReActState':
    """ReAct推理智能体 - 负责思考和决策"""

    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", config.DEFAULT_MAX_ITERATIONS)
    user_message = state.get("current_problem", "")

    print(f"\n🧠 [步骤{current_iter + 1}] 开始推理...")

    # 🆕 智能推理策略选择
    if current_iter == 0:  # 第一轮推理时分析问题并选择策略
        # 获取可用工具信息
        available_tools = get_react_tools()
        available_tool_names = [tool.name for tool in available_tools]

        complexity_result = strategy_manager.analyze_problem_complexity(
            user_message, llm=llm, available_tools=available_tool_names)
        complexity = complexity_result.complexity
        recommended_tools = complexity_result.recommended_tools
        strategy = strategy_manager.select_strategy(complexity)

        print(f"📊 复杂度: {complexity.value} | 策略: {strategy.value}")
        print(f"🎯 推荐工具: {', '.join(recommended_tools[:3])}")

        # 根据状态中的配置决定是否自动调整最大迭代次数
        auto_adjust = state.get("auto_adjust_iterations",
                                config.AUTO_ADJUST_ITERATIONS)
        if auto_adjust:
            # 🆕 根据迭代控制模式调整迭代次数
            control_mode = getattr(
                config, 'ITERATION_CONTROL_MODE', 'intelligent')

            if control_mode == "strict":
                # 严格模式：按策略限制，不允许超出
                strategy_config = strategy_manager.strategy_configs[strategy]
                max_iter = strategy_config["max_iterations"]

            elif control_mode == "intelligent":
                # 智能模式：基于任务复杂度和需求智能调整
                intelligent_config = getattr(
                    config, 'INTELLIGENT_ADJUSTMENT_CONFIG', {})
                base_iterations = intelligent_config.get("base_iterations", 6)
                max_safe_iterations = intelligent_config.get(
                    "max_safe_iterations", 20)

                # 基础迭代次数
                max_iter = base_iterations

                # 🆕 根据任务复杂度调整
                complexity_multiplier = {
                    ProblemComplexity.SIMPLE: 1.0,
                    ProblemComplexity.MEDIUM: 1.5,
                    ProblemComplexity.COMPLEX: 2.0,
                    ProblemComplexity.VERY_COMPLEX: 2.5
                }

                adjusted_iter = int(
                    base_iterations * complexity_multiplier.get(complexity, 1.5))
                max_iter = min(adjusted_iter, max_safe_iterations)

                # 🆕 检查自动扩展条件
                auto_extension_conditions = intelligent_config.get(
                    "auto_extension_conditions", [])
                file_generation_keywords = [
                    "生成", "保存", "创建", "save", "create", ".md", ".pdf", ".doc", ".txt"]

                extension_needed = False
                if "file_generation_required" in auto_extension_conditions:
                    if any(keyword in user_message.lower() for keyword in file_generation_keywords):
                        extension_needed = True
                        print("🔄 检测到文件生成需求，启用智能扩展")

                if "complex_calculation_required" in auto_extension_conditions:
                    calc_keywords = ["计算", "算", "乘", "除",
                                     "加", "减", "求", "math", "calculate"]
                    if any(keyword in user_message.lower() for keyword in calc_keywords):
                        extension_needed = True
                        print("🔄 检测到复杂计算需求，启用智能扩展")

                if extension_needed:
                    max_iter = min(max_iter + 5, max_safe_iterations)  # 额外增加5轮
                    print(f"🔄 智能扩展迭代次数至: {max_iter}")

            elif control_mode == "flexible":
                # 灵活模式：只有安全上限，主要依赖LLM判断
                max_iter = getattr(config, 'INTELLIGENT_ADJUSTMENT_CONFIG', {}).get(
                    "max_safe_iterations", 20)
                print(f"🔄 灵活模式：最大安全迭代次数 {max_iter}")

            else:
                # 默认使用策略配置
                strategy_config = strategy_manager.strategy_configs[strategy]
                max_iter = strategy_config["max_iterations"]

            # 🆕 原有的动态扩展逻辑（仅在非严格模式下生效）
            if control_mode != "strict" and state.get("dynamic_iteration_extension", True):
                # 检查是否有文件生成等复杂要求
                file_generation_keywords = [
                    "生成", "保存", "创建", "save", "create", ".md", ".pdf", ".doc", ".txt"]
                has_complex_requirements = any(
                    keyword in user_message.lower() for keyword in file_generation_keywords)

                if has_complex_requirements or complexity in [ProblemComplexity.COMPLEX, ProblemComplexity.VERY_COMPLEX]:
                    # 根据复杂度和预估步骤数动态调整
                    dynamic_iterations = max(
                        max_iter,
                        complexity_result.estimated_steps + 2,  # 预估步骤数加2个缓冲轮次
                        config.MAX_DYNAMIC_ITERATIONS if hasattr(
                            config, 'MAX_DYNAMIC_ITERATIONS') else 15
                    )

                    # 根据控制模式确定上限
                    if control_mode == "intelligent":
                        upper_limit = getattr(config, 'INTELLIGENT_ADJUSTMENT_CONFIG', {}).get(
                            "max_safe_iterations", 20)
                    else:  # flexible
                        upper_limit = 25  # 灵活模式允许更多轮次

                    dynamic_iterations = min(dynamic_iterations, upper_limit)

                    if dynamic_iterations > max_iter:
                        print(
                            f"🔄 动态扩展迭代次数: {max_iter} -> {dynamic_iterations} (复杂任务需要)")
                        max_iter = dynamic_iterations

            state["max_iterations"] = max_iter
            print(f"🔧 迭代控制模式: {control_mode} | 最大迭代次数: {max_iter}")
        else:
            # 禁用自动调整时使用默认值
            max_iter = config.DEFAULT_MAX_ITERATIONS

        # 更新状态中的策略信息
        state["reasoning_strategy"] = strategy.value
        state["problem_complexity"] = complexity.value
        state["recommended_tools"] = recommended_tools
        state["success_criteria"] = complexity_result.success_criteria
        success_criteria = complexity_result.success_criteria
    else:
        # 从状态中恢复策略信息
        strategy = ReasoningStrategy(
            state.get("reasoning_strategy", "sequential"))
        complexity = ProblemComplexity(
            state.get("problem_complexity", "medium"))
        recommended_tools = state.get("recommended_tools", [])
        success_criteria = state.get("success_criteria", "完成问题解答")

    if current_iter >= max_iter:
        # 🆕 在智能模式下，检查是否真的需要停止
        control_mode = getattr(config, 'ITERATION_CONTROL_MODE', 'intelligent')

        if control_mode == "intelligent":
            # 智能模式：检查任务完成度和进展情况
            intelligent_config = getattr(
                config, 'INTELLIGENT_ADJUSTMENT_CONFIG', {})
            max_safe_iterations = intelligent_config.get(
                "max_safe_iterations", 20)

            # 如果还没达到安全上限，检查是否有继续的必要
            if current_iter < max_safe_iterations:
                # 检查最近的推理进展
                reasoning_chain = state.get("reasoning_chain", [])
                if len(reasoning_chain) >= 2:
                    # 检查最近几轮是否有实质性进展
                    recent_actions = reasoning_chain[-2:]
                    has_meaningful_progress = any(
                        step.get('observation') and
                        step['observation'] != "等待工具执行结果..." and
                        len(step['observation']) > 50
                        for step in recent_actions
                    )

                    if has_meaningful_progress:
                        print(f"🔄 智能模式检测到进展，延长推理至第 {current_iter + 1} 轮")
                        # 临时扩展一轮，让LLM判断是否需要继续
                        state["max_iterations"] = current_iter + 2
                        max_iter = current_iter + 2
                    else:
                        print(f"⏰ 智能模式检测到进展停滞，结束推理")
                        final_answer = f"基于{max_iter}轮推理的结果，未能在当前轮次内完全解决问题"
                        ai_message = AIMessage(content=final_answer)
                        return {
                            **state,
                            "messages": state["messages"] + [ai_message],
                            "next_action": "end"
                        }
                else:
                    print(f"⏰ 达到策略限制轮次({max_iter})，但智能模式允许继续")
                    # 允许继续，但提醒接近限制
                    if current_iter < max_safe_iterations:
                        state["max_iterations"] = current_iter + 3  # 再给3轮机会
                        max_iter = current_iter + 3
            else:
                print(f"⏰ 达到安全上限({max_safe_iterations})，强制结束推理")
                final_answer = f"已达到安全上限({max_safe_iterations})轮，基于已有信息提供答案"
                ai_message = AIMessage(content=final_answer)
                return {
                    **state,
                    "messages": state["messages"] + [ai_message],
                    "next_action": "end"
                }

        elif control_mode == "flexible":
            # 灵活模式：主要依赖LLM判断，只有安全上限
            flexible_limit = getattr(config, 'INTELLIGENT_ADJUSTMENT_CONFIG', {}).get(
                "max_safe_iterations", 20)
            if current_iter >= flexible_limit:
                print(f"⏰ 灵活模式达到安全上限({flexible_limit})，结束推理")
                final_answer = f"已达到安全上限({flexible_limit})轮，基于已有信息提供答案"
                ai_message = AIMessage(content=final_answer)
                return {
                    **state,
                    "messages": state["messages"] + [ai_message],
                    "next_action": "end"
                }
            else:
                print(f"🔄 灵活模式允许继续推理 (第 {current_iter + 1} 轮)")
                # 不强制停止，让LLM决定

        else:  # strict mode
            print(f"⏰ 严格模式达到最大轮次({max_iter})，结束推理")
            ai_message = AIMessage(
                content=f"已达到最大推理轮次({max_iter})，结束思考过程。\n\n基于已有信息，我的最终答案是:\n{state.get('final_answer', '抱歉，无法在限定轮次内完全解决这个问题。')}"
            )
            return {
                **state,
                "messages": state["messages"] + [ai_message],
                "next_action": "end"
            }

    # 🆕 构建推理上下文对象
    available_tools = get_react_tools()
    available_tool_names = [tool.name for tool in available_tools]
    used_tools = state.get("tools_used", [])

    reasoning_context = ReasoningContext(
        problem=user_message,
        complexity=complexity,
        strategy=strategy,
        max_iterations=max_iter,
        current_iteration=current_iter,
        reasoning_chain=state.get("reasoning_chain", []),
        available_tools=available_tool_names,
        used_tools=used_tools,
        confidence_threshold=strategy_manager.strategy_configs[strategy]["confidence_threshold"],
        recommended_tools=recommended_tools
    )

    # 🆕 评估推理进展
    progress_evaluation = strategy_manager.evaluate_reasoning_progress(
        reasoning_context)
    print(
        f"📈 进展: {progress_evaluation['progress_score']:.2f} | 信心: {progress_evaluation['confidence']:.2f}")

    # 如果配置了LLM，使用智能推理
    if llm:
        try:
            # 生成工具文档
            tool_docs = mcp_adapter.generate_tool_documentation()

            # 🆕 使用策略管理器生成智能提示词
            strategy_prompt = strategy_manager.generate_strategy_prompt(
                reasoning_context)

            # 🆕 获取下一步行动建议
            action_suggestions = strategy_manager.suggest_next_action(
                reasoning_context, progress_evaluation)

            # 🆕 计算当前推理阶段
            progress_ratio = current_iter / max_iter if max_iter > 0 else 0
            if progress_ratio < 0.4:
                current_stage = "early_stage"
                stage_description = "信息收集和问题分析阶段"
                stage_priority = "重点进行问题分析、信息搜索和基础计算"
            elif progress_ratio < 0.8:
                current_stage = "middle_stage"
                stage_description = "信息处理和内容生成阶段"
                stage_priority = "重点进行内容生成、文本处理和数据验证"
            else:
                current_stage = "late_stage"
                stage_description = "最终输出和报告生成阶段"
                stage_priority = "重点进行报告生成、格式化和文件保存"

            prompt = f"""
{strategy_prompt}

可用的工具:
{tool_docs}

📊 当前推理状态:
- 进展分数: {progress_evaluation['progress_score']}
- 信心度: {progress_evaluation['confidence']}
- 工具多样性: {progress_evaluation['tool_diversity']}
- 推理阶段: {stage_description}

💡 推理建议:
- 推理焦点: {action_suggestions['reasoning_focus']}
- 推荐工具: {', '.join(action_suggestions['recommended_tools'][:3])}
- 行动类型: {action_suggestions['action_type']}

🎯 推荐工具: {', '.join(recommended_tools)} (基于问题复杂度分析得出)
✅ 成功标准: {success_criteria}

⚠️ 当前阶段重点: {stage_priority}

📋 工具使用指导:
- 如果用户要求生成文件或报告，请在收集足够信息后再进行
- 报告生成工具(如create_markdown_report)应该在最后阶段使用
- 先通过其他工具收集和处理信息，再进行最终的格式化输出

请分析问题并决定下一步行动：

核心目标：理解用户的真实需求并找到最佳解决方案

思考要点：
1. 用户想要什么样的结果？
2. 用户有什么具体的要求或期望？
3. 现在已经获得的信息是否足够回答用户的问题？
4. 是否满足了上述成功标准的所有要求？
5. 用户是否要求特定的输出格式或文件生成？
6. 如果不够，还需要什么信息或操作？

判断完成的标准：
- 不仅要有足够的信息，还要确保完成了用户的所有具体要求
- 特别注意用户是否要求生成文件、报告或特定格式的输出
- 确保每个步骤都按用户要求执行完毕

你可以：
- 使用工具获取更多信息
- 使用工具生成用户要求的输出格式
- 基于已有信息给出最终答案（仅当真正完成所有要求时）

工具选择建议：
- 根据实际需要选择合适的工具
- 数学计算建议使用calculate_math工具确保准确性
- 时间相关信息建议使用时间工具获取准确数据
- 如果用户要求特定格式输出，必须使用相应的格式化工具

请用JSON格式返回你的决定:
{{
    "thought": "详细的思考过程和分析",
    "action": "下一步行动的具体描述",
    "tool_name": "工具名称(如果需要使用工具)",
    "tool_args": {{"参数名": "参数值"}},
    "need_more_info": true/false,
    "final_answer": "最终答案(如果已经可以给出完整答案)"
}}

只返回JSON格式内容。"""

            print(f"🤖 向LLM发送提示词:")
            if current_iter == 0:  # 只在第一轮打印核心问题
                print(f"❓ 核心问题: {user_message}")
            print(f"📏 提示词长度: {len(prompt)} 字符")

            response = await llm.ainvoke([HumanMessage(content=prompt)])

            # 解析LLM响应
            import json
            try:
                content = str(response.content).strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]

                reasoning = json.loads(content.strip())
                thought = reasoning.get("thought", "思考中...")
                action = reasoning.get("action", "执行操作")
                tool_name = reasoning.get("tool_name", "")
                tool_args = reasoning.get("tool_args", {})
                need_more_info = reasoning.get("need_more_info", True)
                final_answer = reasoning.get("final_answer", "")

                print(f"💭 LLM思考: {thought[:100]}...")
                print(f"🎯 决策: {action}")

                # 检查是否完成推理 - 让LLM自主判断任务完成
                if not need_more_info and not tool_name:
                    print("✅ 推理完成")
                    final_answer = final_answer or thought

                    ai_message = AIMessage(
                        content=f"思考完成！\n\n思路: {thought}\n\n最终答案: {final_answer}"
                    )

                    reasoning_chain = state.get("reasoning_chain", [])
                    return {
                        **state,
                        "messages": state["messages"] + [ai_message],
                        "final_answer": final_answer,
                        "thought_process": state["thought_process"] + [thought],
                        "reasoning_chain": reasoning_chain,
                        "next_action": "end"
                    }

                # 如果LLM指定了工具，无论need_more_info如何都应该先执行工具
                if tool_name:
                    print(f"🔧 调用工具: {tool_name}")
                    tool_name = resolve_tool_name(tool_name)
                    tool_args = resolve_params(tool_name, tool_args)
                    print(f"📋 工具参数: {tool_args}")

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

                else:
                    print("❌ LLM没有指定工具或明确完成，继续推理")
                    ai_message = AIMessage(
                        content=f"第{current_iter + 1}轮推理:\n\n🤔 思考: {thought}\n\n📝 行动: {action}\n\n继续推理..."
                    )

                    return {
                        **state,
                        "messages": state["messages"] + [ai_message],
                        "thought_process": state["thought_process"] + [thought],
                        "current_iteration": current_iter + 1,
                        "next_action": "continue_reasoning"
                    }

            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ 解析LLM响应失败: {e}")
                ai_message = AIMessage(
                    content=f"第{current_iter + 1}轮推理失败，JSON解析错误: {e}"
                )
                return {
                    **state,
                    "messages": state["messages"] + [ai_message],
                    "current_iteration": current_iter + 1,
                    "next_action": "continue_reasoning"
                }

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            ai_message = AIMessage(
                content=f"第{current_iter + 1}轮推理失败: {str(e)}"
            )
            return {
                **state,
                "messages": state["messages"] + [ai_message],
                "current_iteration": current_iter + 1,
                "next_action": "continue_reasoning"
            }

    else:
        print("⚠️ 未配置LLM，无法进行推理")
        ai_message = AIMessage(content="未配置LLM，无法进行推理")
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "next_action": "end"
        }


async def react_executor_agent(state: 'ReActState') -> 'ReActState':
    """ReAct执行智能体 - 负责处理工具执行结果"""

    print(f"\n🔧 [步骤{state.get('current_iteration', 0)}] 处理工具结果...")

    # 获取最后一条消息（工具执行结果）
    last_message = state["messages"][-1]
    tool_output = str(last_message.content)  # 确保是字符串类型

    # 显示工具执行结果摘要
    if len(tool_output) > 200:
        result_summary = tool_output[:200] + "..."
    else:
        result_summary = tool_output

    print(f"📋 工具执行结果: {result_summary}")

    # 更新推理链中的观察结果
    reasoning_chain = state.get("reasoning_chain", [])
    if reasoning_chain:
        reasoning_chain[-1]["observation"] = tool_output

    # 获取当前问题和上下文
    current_problem = state.get("current_problem", "")
    current_iter = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", config.DEFAULT_MAX_ITERATIONS)
    reached_max_iter = current_iter >= max_iter

    # 🆕 文件存在性检查函数
    def check_file_requirements(problem: str, tool_output: str) -> Dict[str, Any]:
        """检查文件生成要求是否满足"""
        import os
        import re

        # 检测文件生成要求
        file_generation_keywords = ["生成", "保存", "创建", "save", "create"]
        file_extension_pattern = r'\.(md|pdf|doc|docx|txt|json|xml|html|csv|xlsx)(?:\s|$|，|。|！|？)'

        has_file_requirement = any(keyword in problem.lower()
                                   for keyword in file_generation_keywords)
        file_extensions = re.findall(file_extension_pattern, problem.lower())

        # 从问题中提取可能的文件名
        potential_filenames = []

        # 匹配 "保存为 filename.ext" 或 "save as filename.ext" 模式
        # 支持中文文件名的正则表达式
        filename_patterns = [
            r'保存为\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'save\s+as\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'创建\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'create\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'生成\s+([^\s]+\.[a-zA-Z0-9]+)',
            r'([^\s]+\.[a-zA-Z0-9]+)(?:\s|$|，|。)'
        ]

        for pattern in filename_patterns:
            matches = re.findall(pattern, problem, re.IGNORECASE)
            potential_filenames.extend(matches)

        # 从工具输出中提取可能创建的文件
        output_filenames = []
        output_patterns = [
            r'文件已保存为[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'文件已保存到[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'已保存到[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'文件已创建[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'saved as[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'saved to[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'created[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'文件路径[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'file path[：:\s]+([^\s]+\.[a-zA-Z0-9]+)',
            r'file_path[\"\':\s]+([^\s\"\']+\.[a-zA-Z0-9]+)'
        ]

        for pattern in output_patterns:
            matches = re.findall(pattern, tool_output, re.IGNORECASE)
            output_filenames.extend(matches)

        # 检查文件是否真的存在
        existing_files = []
        missing_files = []

        all_potential_files = list(set(potential_filenames + output_filenames))

        for filename in all_potential_files:
            if os.path.exists(filename):
                existing_files.append(filename)
            else:
                missing_files.append(filename)

        return {
            "has_file_requirement": has_file_requirement,
            "file_extensions": file_extensions,
            "potential_filenames": potential_filenames,
            "output_filenames": output_filenames,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "requirement_satisfied": has_file_requirement and len(existing_files) > 0
        }

    # 如果配置了LLM，让LLM判断是否继续推理
    if llm:
        try:
            # 构建推理上下文
            context = f"问题: {current_problem}\n\n"
            if reasoning_chain:
                context += "推理过程:\n"
                for i, step in enumerate(reasoning_chain, 1):
                    context += f"第{i}轮:\n"
                    context += f"思考: {step.get('thought', '')}\n"
                    context += f"行动: {step.get('action', '')}\n"
                    context += f"观察: {step.get('observation', '')}\n\n"

            # 🆕 执行文件检查
            file_check_result = check_file_requirements(
                current_problem, tool_output)

            # 如果达到最大迭代次数，需要给出最终答案
            if reached_max_iter:
                prompt = f"""
⏰ 已达到最大推理轮次({max_iter})，现在需要给出最终答案。

{context}

最新的工具执行结果: {tool_output}

🗂️ 文件生成检查结果:
- 是否有文件生成要求: {file_check_result['has_file_requirement']}
- 期望的文件: {file_check_result['potential_filenames']}
- 输出中提到的文件: {file_check_result['output_filenames']}
- 实际存在的文件: {file_check_result['existing_files']}
- 缺失的文件: {file_check_result['missing_files']}

请基于已获得的所有信息给出最终答案。根据你的分析，尽力给出最佳的答案。

请用JSON格式返回你的决定:
{{
    "analysis": "对当前结果的分析",
    "is_complete": true,
    "final_answer": "基于已有信息的最终答案",
    "next_step": "无"
}}

只返回JSON格式内容。"""
            else:
                # 获取成功标准
                success_criteria = state.get("success_criteria", "完成问题解答")

                prompt = f"""
当前是第{current_iter}轮推理的结果分析。

{context}

最新的工具执行结果: {tool_output}

✅ 成功标准: {success_criteria}

🗂️ 文件生成检查结果:
- 是否有文件生成要求: {file_check_result['has_file_requirement']}
- 期望的文件: {file_check_result['potential_filenames']}
- 输出中提到的文件: {file_check_result['output_filenames']}
- 实际存在的文件: {file_check_result['existing_files']}
- 缺失的文件: {file_check_result['missing_files']}
- 文件要求是否满足: {file_check_result['requirement_satisfied']}

请分析当前情况并决定下一步：

**🔍 严格检查清单：**
1. 用户的原始问题是什么？
2. 用户是否明确要求了特定的输出格式或文件？
3. 是否需要生成文件或报告？如果是，文件是否已经实际存在？
4. 是否需要保存到特定文件名？如果是，该文件是否已经存在？
5. 所有用户明确提出的要求是否都已经满足？

**❗️ 特别注意 - 文件生成要求：**
- 如果用户要求生成文件，必须确认文件确实存在于文件系统中
- 仅仅工具说"已保存"是不够的，必须有实际的文件存在
- 如果有文件生成要求但文件不存在，任务未完成
- 检查文件路径和文件名是否正确

**🎯 决策规则：**
- 只有在所有用户要求都已经完成时，才能标记为完成
- 如果用户要求生成文件但文件不存在，必须继续推理
- 如果还有任何未完成的要求，必须继续推理和使用工具

请用JSON格式返回你的决定:
{{
    "analysis": "详细分析当前状态和每个用户要求的完成情况",
    "is_complete": true/false,
    "final_answer": "最终答案的完整描述(如果完成)",
    "next_step": "下一步具体计划(如果需要继续)"
}}

只返回JSON格式内容。"""

            print(f"🤖 向LLM发送分析请求:")
            print(f"❓ 分析任务: 基于工具执行结果和文件检查，是否能够完成任务")
            print(f"📏 提示词长度: {len(prompt)} 字符")

            # 🆕 显示文件检查结果
            if file_check_result['has_file_requirement']:
                print(
                    f"📁 文件生成要求: {'✅ 已满足' if file_check_result['requirement_satisfied'] else '❌ 未满足'}")
                if file_check_result['existing_files']:
                    print(
                        f"📄 已存在文件: {', '.join(file_check_result['existing_files'])}")
                if file_check_result['missing_files']:
                    print(
                        f"❌ 缺失文件: {', '.join(file_check_result['missing_files'])}")

            response = await llm.ainvoke([HumanMessage(content=prompt)])

            # 解析LLM响应
            import json
            try:
                content = str(response.content).strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]

                decision = json.loads(content.strip())
                analysis = decision.get("analysis", "分析工具执行结果")
                is_complete = decision.get("is_complete", False)
                final_answer = decision.get("final_answer", "")
                next_step = decision.get("next_step", "")

                print(f"💭 LLM分析: {analysis[:100]}...")
                print(f"🎯 是否完成: {is_complete}")

                # 🆕 强制文件检查：如果有文件生成要求但文件不存在，强制继续推理
                if file_check_result['has_file_requirement'] and not file_check_result['requirement_satisfied']:
                    print("⚠️ 检测到文件生成要求但文件不存在，强制继续推理")
                    is_complete = False
                    if not next_step:
                        next_step = "必须确保文件生成工具真正创建了文件"
                    analysis = f"文件生成要求未满足：{file_check_result['missing_files']}"

                if is_complete and final_answer:
                    print("✅ 推理完成")

                    # 🆕 添加结果质量评估和优化建议
                    quality_assessment = ""
                    if config.ENABLE_RESULT_QUALITY_ASSESSMENT:
                        quality_assessment = await evaluate_result_quality(
                            current_problem, final_answer, reasoning_chain, file_check_result, llm
                        )

                    ai_message = AIMessage(
                        content=f"✅ 推理完成！\n\n观察: {tool_output}\n\n分析: {analysis}\n\n最终答案: {final_answer}\n\n{quality_assessment}"
                    )

                    return {
                        **state,
                        "messages": state["messages"] + [ai_message],
                        "final_answer": final_answer,
                        "observations": state["observations"] + [tool_output],
                        "reasoning_chain": reasoning_chain,
                        "next_action": "end"
                    }
                elif reached_max_iter:
                    print("⏰ 达到最大轮次，结束推理")
                    final_answer = final_answer or f"基于{max_iter}轮推理的结果: {analysis}"

                    # 🆕 添加结果质量评估和优化建议
                    quality_assessment = ""
                    if config.ENABLE_RESULT_QUALITY_ASSESSMENT:
                        quality_assessment = await evaluate_result_quality(
                            current_problem, final_answer, reasoning_chain, file_check_result, llm
                        )

                    ai_message = AIMessage(
                        content=f"⏰ 达到最大推理轮次。\n\n观察: {tool_output}\n\n分析: {analysis}\n\n最终答案: {final_answer}\n\n{quality_assessment}"
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
                    print("🔄 继续推理")
                    ai_message = AIMessage(
                        content=f"观察: {tool_output}\n\n分析: {analysis}\n\n下一步: {next_step}\n\n继续推理..."
                    )

                    return {
                        **state,
                        "messages": state["messages"] + [ai_message],
                        "observations": state["observations"] + [tool_output],
                        "reasoning_chain": reasoning_chain,
                        "current_iteration": current_iter + 1,
                        "next_action": "continue_reasoning"
                    }

            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ 解析LLM响应失败: {e}")
                ai_message = AIMessage(
                    content=f"观察: {tool_output}\n\n解析响应失败: {e}\n\n继续推理..."
                )
                return {
                    **state,
                    "messages": state["messages"] + [ai_message],
                    "observations": state["observations"] + [tool_output],
                    "reasoning_chain": reasoning_chain,
                    "current_iteration": current_iter + 1,
                    "next_action": "continue_reasoning"
                }

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            ai_message = AIMessage(
                content=f"观察: {tool_output}\n\n分析失败: {str(e)}\n\n继续推理..."
            )
            return {
                **state,
                "messages": state["messages"] + [ai_message],
                "observations": state["observations"] + [tool_output],
                "reasoning_chain": reasoning_chain,
                "current_iteration": current_iter + 1,
                "next_action": "continue_reasoning"
            }

    else:
        print("⚠️ 未配置LLM，无法判断是否继续推理")
        ai_message = AIMessage(
            content=f"观察: {tool_output}\n\n未配置LLM，继续推理..."
        )
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "observations": state["observations"] + [tool_output],
            "reasoning_chain": reasoning_chain,
            "current_iteration": current_iter + 1,
            "next_action": "continue_reasoning"
        }
