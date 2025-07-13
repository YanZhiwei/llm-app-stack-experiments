"""
推理策略模块 - 提供多种推理策略和自适应选择机制
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from config import config

# 导入工具分类信息
try:
    from tools import get_tool_categories
except ImportError:
    # 如果导入失败，提供默认的工具分类
    def get_tool_categories():
        return {
            "核心工具": [
                "search_information - 搜索信息",
                "calculate_math - 数学计算",
                "analyze_problem - 问题分析",
                "store_memory - 存储记忆",
                "retrieve_memory - 检索记忆",
                "verify_answer - 验证答案"
            ]
        }


class ReasoningStrategy(Enum):
    """推理策略枚举"""
    SEQUENTIAL = "sequential"  # 顺序推理
    PARALLEL = "parallel"  # 并行推理
    HIERARCHICAL = "hierarchical"  # 层次推理
    ADAPTIVE = "adaptive"  # 自适应推理
    FOCUSED = "focused"  # 聚焦推理
    EXPLORATORY = "exploratory"  # 探索推理


class ProblemComplexity(Enum):
    """问题复杂度枚举"""
    SIMPLE = "simple"  # 简单问题
    MEDIUM = "medium"  # 中等复杂度
    COMPLEX = "complex"  # 复杂问题
    VERY_COMPLEX = "very_complex"  # 极复杂问题


@dataclass
class ComplexityAnalysisResult:
    """复杂度分析结果"""
    complexity: ProblemComplexity
    reasoning: str
    estimated_steps: int
    recommended_tools: List[str]
    tool_availability_impact: str
    success_criteria: str = "完成问题解答"


@dataclass
class ReasoningContext:
    """推理上下文"""
    problem: str
    complexity: ProblemComplexity
    strategy: ReasoningStrategy
    max_iterations: int
    current_iteration: int
    reasoning_chain: List[Dict[str, str]]
    available_tools: List[str]
    used_tools: List[str]
    confidence_threshold: float = 0.8
    time_limit: Optional[int] = None  # 秒
    recommended_tools: Optional[List[str]] = None  # LLM推荐的工具


class ReasoningStrategyManager:
    """推理策略管理器"""

    def __init__(self):
        self.strategy_configs = {
            ReasoningStrategy.SEQUENTIAL: {
                "description": "顺序推理：逐步分析，一步一步解决问题",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["sequential"],
                "confidence_threshold": 0.7,
                "tool_selection": "conservative",
                "suitable_for": ["simple", "medium"]
            },
            ReasoningStrategy.PARALLEL: {
                "description": "并行推理：同时考虑多个解决路径",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["parallel"],
                "confidence_threshold": 0.8,
                "tool_selection": "aggressive",
                "suitable_for": ["complex", "very_complex"]
            },
            ReasoningStrategy.HIERARCHICAL: {
                "description": "层次推理：分解为子问题，逐层解决",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["hierarchical"],
                "confidence_threshold": 0.75,
                "tool_selection": "structured",
                "suitable_for": ["complex", "very_complex"]
            },
            ReasoningStrategy.ADAPTIVE: {
                "description": "自适应推理：根据进展动态调整策略",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["adaptive"],
                "confidence_threshold": 0.8,
                "tool_selection": "dynamic",
                "suitable_for": ["medium", "complex", "very_complex"]
            },
            ReasoningStrategy.FOCUSED: {
                "description": "聚焦推理：专注于最关键的信息",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["focused"],
                "confidence_threshold": 0.85,
                "tool_selection": "targeted",
                "suitable_for": ["simple", "medium"]
            },
            ReasoningStrategy.EXPLORATORY: {
                "description": "探索推理：广泛搜索，发现新的可能性",
                "max_iterations": config.STRATEGY_MAX_ITERATIONS["exploratory"],
                "confidence_threshold": 0.7,
                "tool_selection": "exploratory",
                "suitable_for": ["complex", "very_complex"]
            }
        }

    def analyze_problem_complexity_with_llm(self, problem: str, llm=None, available_tools: Optional[List[str]] = None) -> ComplexityAnalysisResult:
        """使用LLM分析问题复杂度"""

        if not llm:
            print("⚠️ 未配置LLM，返回默认复杂度")
            return ComplexityAnalysisResult(
                complexity=ProblemComplexity.MEDIUM,
                reasoning="未配置LLM，使用默认复杂度",
                estimated_steps=3,
                recommended_tools=[],
                tool_availability_impact="无法分析工具影响",
                success_criteria="完成问题解答"
            )

        try:
            print("🤖 LLM分析问题复杂度...")

            # 动态生成工具信息
            tool_info = self._generate_tool_info(available_tools)

            prompt = f"""
请分析以下问题，帮助制定最佳的解决策略：

问题: {problem}

{tool_info}

请从以下角度分析这个问题：

1. 问题的本质和核心需求
2. 需要获取哪些信息？
3. 需要进行哪些处理步骤？
4. 可以使用哪些工具来简化解决过程？
5. 用户的期望结果是什么？

**🎯 特别重要 - 输出格式检查：**
- 用户是否要求生成文件？(如.md, .pdf, .doc等)
- 用户是否要求特定格式的输出？(如表格、报告等)
- 用户是否要求保存到特定文件名？

如果用户有任何文件生成或格式输出要求，必须将相应的工具列入推荐工具列表！

基于你的分析，请评估问题的复杂程度：
- SIMPLE: 简单直接，可以快速解决
- MEDIUM: 中等复杂度，需要一些步骤
- COMPLEX: 比较复杂，需要多个步骤协调
- VERY_COMPLEX: 非常复杂，需要深入分析

请用JSON格式返回分析结果：
{{
    "complexity": "SIMPLE|MEDIUM|COMPLEX|VERY_COMPLEX",
    "reasoning": "你的分析思路和理由",
    "estimated_steps": 预估需要的步骤数,
    "required_tools": ["推荐使用的工具列表"],
    "tool_availability_impact": "工具对解决问题的帮助说明",
    "success_criteria": "怎样才算成功解决了这个问题"
}}

只返回JSON格式内容。
"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])

            import json
            content = str(response.content).strip()

            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]

            result = json.loads(content.strip())
            complexity_str = result.get("complexity", "MEDIUM")
            reasoning = result.get("reasoning", "")
            estimated_steps = result.get("estimated_steps", 0)
            required_tools = result.get("required_tools", [])
            tool_impact = result.get("tool_availability_impact", "")
            success_criteria = result.get("success_criteria", "完成问题解答")

            print(f"📊 复杂度分析: {complexity_str} | 预估步骤: {estimated_steps}")
            print(f"🎯 推荐工具: {', '.join(required_tools)}")
            print(f"✅ 成功标准: {success_criteria}")

            # 转换为枚举值
            complexity_mapping = {
                "SIMPLE": ProblemComplexity.SIMPLE,
                "MEDIUM": ProblemComplexity.MEDIUM,
                "COMPLEX": ProblemComplexity.COMPLEX,
                "VERY_COMPLEX": ProblemComplexity.VERY_COMPLEX
            }

            final_complexity = complexity_mapping.get(
                complexity_str, ProblemComplexity.MEDIUM)

            # 🆕 检查是否有文件生成要求，如果有则自动提高复杂度
            file_generation_keywords = ["生成", "保存", "创建", "save", "create",
                                        ".md", ".pdf", ".doc", ".txt", ".json", ".xml", ".html"]
            has_file_generation_requirement = any(
                keyword in problem.lower() for keyword in file_generation_keywords)

            if has_file_generation_requirement:
                # 自动提高复杂度等级
                if final_complexity == ProblemComplexity.SIMPLE:
                    final_complexity = ProblemComplexity.MEDIUM
                    print("🔄 检测到文件生成要求，复杂度从SIMPLE提升到MEDIUM")
                elif final_complexity == ProblemComplexity.MEDIUM:
                    final_complexity = ProblemComplexity.COMPLEX
                    print("🔄 检测到文件生成要求，复杂度从MEDIUM提升到COMPLEX")
                elif final_complexity == ProblemComplexity.COMPLEX:
                    final_complexity = ProblemComplexity.VERY_COMPLEX
                    print("🔄 检测到文件生成要求，复杂度从COMPLEX提升到VERY_COMPLEX")

                # 相应增加预估步骤数
                estimated_steps = max(
                    estimated_steps + 2, 6)  # 至少6步确保有足够时间生成文件
                print(f"🔄 预估步骤数调整为: {estimated_steps}")

                # 确保推荐工具中包含文件生成工具
                file_generation_tools = [
                    "create_markdown_report", "create_markdown_table", "format_markdown_content"]
                if available_tools:
                    available_file_tools = [
                        tool for tool in file_generation_tools if tool in available_tools]
                    for tool in available_file_tools:
                        if tool not in required_tools:
                            required_tools.append(tool)
                            print(f"🔄 自动添加文件生成工具: {tool}")

            return ComplexityAnalysisResult(
                complexity=final_complexity,
                reasoning=reasoning,
                estimated_steps=estimated_steps,
                recommended_tools=required_tools,
                tool_availability_impact=tool_impact,
                success_criteria=success_criteria
            )

        except Exception as e:
            print(f"❌ LLM复杂度分析失败: {e}")
            return ComplexityAnalysisResult(
                complexity=ProblemComplexity.MEDIUM,
                reasoning=f"LLM分析失败: {e}",
                estimated_steps=3,
                recommended_tools=[],
                tool_availability_impact="无法分析工具影响",
                success_criteria="完成问题解答"
            )

    def _generate_tool_info(self, available_tools: Optional[List[str]] = None) -> str:
        """动态生成工具信息"""
        if not available_tools:
            return "⚠️ 未提供可用工具信息"

        # 获取工具分类信息
        tool_categories = get_tool_categories()

        # 提取工具名称（移除描述部分）
        def extract_tool_name(tool_desc: str) -> str:
            """从 'tool_name - description' 格式中提取工具名称"""
            return tool_desc.split(' - ')[0].strip()

        # 过滤可用工具
        available_tool_info = []
        available_tool_info.append(f"当前可用工具：{', '.join(available_tools)}")
        available_tool_info.append("")
        available_tool_info.append("主要工具类型：")

        for category, tools in tool_categories.items():
            # 过滤出在available_tools中的工具
            available_category_tools = []
            for tool_desc in tools:
                tool_name = extract_tool_name(tool_desc)
                if tool_name in available_tools:
                    available_category_tools.append(tool_desc)

            # 如果该分类有可用工具，则添加到信息中
            if available_category_tools:
                available_tool_info.append(
                    f"- {category}：{', '.join(available_category_tools)}")

        # 添加额外的工具（不在分类中的）
        categorized_tools = set()
        for category, tools in tool_categories.items():
            for tool_desc in tools:
                tool_name = extract_tool_name(tool_desc)
                categorized_tools.add(tool_name)

        uncategorized_tools = [
            tool for tool in available_tools if tool not in categorized_tools]
        if uncategorized_tools:
            available_tool_info.append(
                f"- 其他工具：{', '.join(uncategorized_tools)}")

        return "\n".join(available_tool_info)

    def select_strategy(self, complexity: ProblemComplexity, context: Optional[Dict[str, Any]] = None) -> ReasoningStrategy:
        """根据问题复杂度选择最佳推理策略"""

        # 基于复杂度的策略映射
        strategy_mapping = {
            ProblemComplexity.SIMPLE: ReasoningStrategy.FOCUSED,
            ProblemComplexity.MEDIUM: ReasoningStrategy.SEQUENTIAL,
            ProblemComplexity.COMPLEX: ReasoningStrategy.HIERARCHICAL,
            ProblemComplexity.VERY_COMPLEX: ReasoningStrategy.ADAPTIVE
        }

        # 考虑上下文因素
        if context:
            # 如果时间紧迫，选择更快的策略
            # 5分钟
            if context.get("time_limit") and context["time_limit"] < 300:
                if complexity in [ProblemComplexity.COMPLEX, ProblemComplexity.VERY_COMPLEX]:
                    return ReasoningStrategy.FOCUSED

            # 如果之前的推理失败，切换到探索策略
            if context.get("previous_failures", 0) > 1:
                return ReasoningStrategy.EXPLORATORY

            # 如果工具使用受限，选择保守策略
            if context.get("tool_limit") and context["tool_limit"] < 5:
                return ReasoningStrategy.FOCUSED

        return strategy_mapping.get(complexity, ReasoningStrategy.SEQUENTIAL)

    def analyze_problem_complexity(self, problem: str, context: Optional[Dict[str, Any]] = None, llm=None, available_tools: Optional[List[str]] = None) -> ComplexityAnalysisResult:
        """分析问题复杂度的主要入口方法"""
        return self.analyze_problem_complexity_with_llm(problem, llm, available_tools)

    def generate_strategy_prompt(self, context: ReasoningContext) -> str:
        """生成针对特定策略的提示词"""

        strategy_config = self.strategy_configs[context.strategy]

        base_prompt = f"""
你正在使用【{context.strategy.value}】推理策略解决问题。

策略描述: {strategy_config['description']}
问题复杂度: {context.complexity.value}
当前轮次: {context.current_iteration + 1}/{context.max_iterations}
信心度阈值: {context.confidence_threshold}

用户问题: {context.problem}
"""

        # 根据策略类型添加特定指导
        if context.strategy == ReasoningStrategy.SEQUENTIAL:
            base_prompt += """
【顺序推理策略指导】:
1. 逐步分析问题，一次专注一个方面
2. 确保每一步都有明确的目标
3. 在继续下一步之前验证当前步骤的结果
4. 保持逻辑的连贯性和清晰性
"""

        elif context.strategy == ReasoningStrategy.PARALLEL:
            base_prompt += """
【并行推理策略指导】:
1. 同时考虑多个解决路径
2. 识别可以并行处理的子问题
3. 比较不同方法的优缺点
4. 选择最有希望的路径继续
"""

        elif context.strategy == ReasoningStrategy.HIERARCHICAL:
            base_prompt += """
【层次推理策略指导】:
1. 将复杂问题分解为更小的子问题
2. 建立问题之间的层次关系
3. 从基础问题开始，逐层向上解决
4. 确保子问题的解决方案能够整合
"""

        elif context.strategy == ReasoningStrategy.ADAPTIVE:
            base_prompt += """
【自适应推理策略指导】:
1. 根据当前进展调整推理方向
2. 灵活切换不同的解决方法
3. 监控推理效果，及时调整策略
4. 在必要时改变问题分析角度
"""

        elif context.strategy == ReasoningStrategy.FOCUSED:
            base_prompt += """
【聚焦推理策略指导】:
1. 专注于最关键的信息和要求
2. 避免不必要的复杂化
3. 直接针对核心问题寻找解决方案
4. 提高推理的效率和准确性
"""

        elif context.strategy == ReasoningStrategy.EXPLORATORY:
            base_prompt += """
【探索推理策略指导】:
1. 广泛搜索可能的解决方案
2. 尝试不同的方法和角度
3. 不要过早排除任何可能性
4. 从多个维度验证结果
"""

        # 添加推理历史
        if context.reasoning_chain:
            base_prompt += "\n之前的推理过程:\n"
            for i, step in enumerate(context.reasoning_chain, 1):
                base_prompt += f"第{i}轮:\n"
                base_prompt += f"思考: {step.get('thought', '')}\n"
                base_prompt += f"行动: {step.get('action', '')}\n"
                base_prompt += f"观察: {step.get('observation', '')}\n\n"

        return base_prompt

    def evaluate_reasoning_progress(self, context: ReasoningContext) -> Dict[str, Any]:
        """评估推理进展"""

        if not context.reasoning_chain:
            return {
                "progress_score": 0.0,
                "confidence": 0.0,
                "should_continue": True,
                "recommendations": ["开始推理过程"],
                "tool_diversity": 0.0,
                "reasoning_depth": 0.0
            }

        # 计算进展分数
        tool_diversity = len(set(context.used_tools)) / max(
            len(context.available_tools), 1) if context.available_tools else 0
        reasoning_depth = len(context.reasoning_chain) / \
            context.max_iterations if context.max_iterations > 0 else 0
        information_gathering = sum(1 for step in context.reasoning_chain
                                    if step.get('observation') and step['observation'] != "等待工具执行结果...")

        progress_indicators = {
            "tool_diversity": tool_diversity,
            "reasoning_depth": reasoning_depth,
            "information_gathering": information_gathering
        }

        progress_score = sum(progress_indicators.values()
                             ) / len(progress_indicators)

        # 估算信心度 - 采用更合理的渐进式计算
        base_confidence = 0.2  # 基础信心度

        # 1. 推理进展信心度 (0-0.3)
        reasoning_progress = min(
            len(context.reasoning_chain) / max(context.max_iterations, 1), 1.0)
        progress_confidence = reasoning_progress * 0.3

        # 2. 工具使用信心度 (0-0.25)
        tool_usage_ratio = len(set(context.used_tools)) / max(
            len(context.available_tools), 1) if context.available_tools else 0
        tool_confidence = min(tool_usage_ratio * 2, 1.0) * 0.25  # 使用多样性工具增加信心

        # 3. 信息获取信心度 (0-0.25)
        valid_observations = sum(1 for step in context.reasoning_chain
                                 if step.get('observation') and
                                 step['observation'] != "等待工具执行结果..." and
                                 len(step['observation']) > 20)
        info_confidence = min(valid_observations / 3,
                              1.0) * 0.25  # 获得3个有效观察结果达到最大信心

        # 4. 推荐工具匹配信心度 (0-0.2)
        recommended_tool_confidence = 0.0
        if context.recommended_tools:
            used_recommended_tools = [
                tool for tool in context.used_tools if tool in context.recommended_tools]
            if used_recommended_tools:
                recommended_tool_confidence = min(
                    len(used_recommended_tools) / len(context.recommended_tools), 1.0) * 0.2

        # 总信心度计算
        confidence = base_confidence + progress_confidence + \
            tool_confidence + info_confidence + recommended_tool_confidence

        # 确保信心度在合理范围内
        confidence = max(0.1, min(confidence, 1.0))  # 至少0.1，最多1.0

        # 决定是否继续
        should_continue = (
            confidence < context.confidence_threshold and
            context.current_iteration < context.max_iterations
        )

        # 生成建议
        recommendations = []

        if progress_score < 0.3:
            recommendations.append("推理进展缓慢，考虑改变策略")

        if len(set(context.used_tools)) < 3 and len(context.available_tools) > 5:
            recommendations.append("尝试使用更多类型的工具")

        if confidence < 0.5:
            recommendations.append("需要收集更多信息")

        if context.current_iteration >= context.max_iterations * 0.8:
            recommendations.append("接近最大轮次，准备总结")

        return {
            "progress_score": round(progress_score, 2),
            "confidence": round(confidence, 2),
            "should_continue": should_continue,
            "recommendations": recommendations,
            "tool_diversity": round(tool_diversity, 2),
            "reasoning_depth": round(reasoning_depth, 2)
        }

    def _get_tool_priority_stages(self) -> Dict[str, List[str]]:
        """定义工具调用的优先级阶段"""
        return {
            "early_stage": [
                "analyze_problem",
                "search_information", 
                "calculate_math",
                "get_current_time",
                "get_weather_info",
                "get_exchange_rate",
                "store_memory",
                "retrieve_memory"
            ],
            "middle_stage": [
                "generate_detailed_content",
                "analyze_text",
                "format_text",
                "extract_patterns",
                "convert_length",
                "convert_weight",
                "convert_temperature",
                "verify_answer",
                "get_ip_location",
                "search_flights"
            ],
            "late_stage": [
                "create_markdown_report",
                "create_markdown_table", 
                "format_markdown_content",
                "create_business_trip_report",
                "create_enhanced_markdown_table",
                "create_text_chart",
                "export_logs_json"
            ]
        }

    def _filter_tools_by_stage(self, tools: List[str], current_iteration: int, max_iterations: int) -> List[str]:
        """根据当前推理阶段过滤工具"""
        stages = self._get_tool_priority_stages()
        
        # 计算当前阶段
        progress_ratio = current_iteration / max_iterations if max_iterations > 0 else 0
        
        if progress_ratio < 0.4:  # 前40%为早期阶段
            preferred_tools = stages["early_stage"]
            allowed_tools = stages["early_stage"] + stages["middle_stage"]
        elif progress_ratio < 0.8:  # 40%-80%为中期阶段
            preferred_tools = stages["middle_stage"]
            allowed_tools = stages["early_stage"] + stages["middle_stage"] + stages["late_stage"]
        else:  # 80%以上为后期阶段
            preferred_tools = stages["late_stage"]
            allowed_tools = stages["early_stage"] + stages["middle_stage"] + stages["late_stage"]
        
        # 优先返回推荐阶段的工具
        stage_filtered_tools = [tool for tool in tools if tool in preferred_tools]
        if stage_filtered_tools:
            return stage_filtered_tools
        
        # 如果没有推荐阶段的工具，返回允许的工具
        return [tool for tool in tools if tool in allowed_tools]

    def suggest_next_action(self, context: ReasoningContext, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """建议下一步行动"""

        suggestions = {
            "priority": "medium",
            "action_type": "continue",
            "recommended_tools": [],
            "reasoning_focus": "",
            "confidence_boost": []
        }

        # 根据策略类型调整建议
        if context.strategy == ReasoningStrategy.SEQUENTIAL:
            if evaluation["progress_score"] < 0.5:
                suggestions["reasoning_focus"] = "专注于当前步骤，确保质量"
            else:
                suggestions["reasoning_focus"] = "继续下一个逻辑步骤"

        elif context.strategy == ReasoningStrategy.HIERARCHICAL:
            if evaluation["tool_diversity"] < 0.3:
                suggestions["reasoning_focus"] = "分解问题为更小的子问题"
            else:
                suggestions["reasoning_focus"] = "整合子问题的解决方案"

        elif context.strategy == ReasoningStrategy.ADAPTIVE:
            if evaluation["confidence"] < 0.6:
                suggestions["action_type"] = "pivot"
                suggestions["reasoning_focus"] = "尝试不同的解决角度"
            else:
                suggestions["reasoning_focus"] = "深化当前方向的分析"

        # 🆕 优先推荐LLM分析得出的工具，但按阶段过滤
        if context.recommended_tools:
            # 过滤出还未使用的推荐工具
            unused_recommended_tools = [
                tool for tool in context.recommended_tools
                if tool not in context.used_tools and tool in context.available_tools
            ]
            
            # 🆕 按阶段过滤工具
            stage_filtered_tools = self._filter_tools_by_stage(
                unused_recommended_tools, 
                context.current_iteration, 
                context.max_iterations
            )

            if stage_filtered_tools:
                suggestions["recommended_tools"] = stage_filtered_tools[:3]
            elif unused_recommended_tools:
                # 如果当前阶段没有合适的工具，但有其他推荐工具，仍然可以使用
                suggestions["recommended_tools"] = unused_recommended_tools[:2]
            else:
                # 如果推荐工具都用完了，按原逻辑选择
                unused_tools = [
                    tool for tool in context.available_tools if tool not in context.used_tools]
                stage_filtered_unused = self._filter_tools_by_stage(
                    unused_tools, context.current_iteration, context.max_iterations)
                
                if context.complexity == ProblemComplexity.SIMPLE:
                    suggestions["recommended_tools"] = stage_filtered_unused[:2]
                elif context.complexity == ProblemComplexity.MEDIUM:
                    suggestions["recommended_tools"] = stage_filtered_unused[:3]
                else:
                    suggestions["recommended_tools"] = stage_filtered_unused[:5]
        else:
            # 如果没有推荐工具，按原逻辑选择但按阶段过滤
            unused_tools = [
                tool for tool in context.available_tools if tool not in context.used_tools]
            stage_filtered_unused = self._filter_tools_by_stage(
                unused_tools, context.current_iteration, context.max_iterations)
            
            if context.complexity == ProblemComplexity.SIMPLE:
                suggestions["recommended_tools"] = stage_filtered_unused[:2]
            elif context.complexity == ProblemComplexity.MEDIUM:
                suggestions["recommended_tools"] = stage_filtered_unused[:3]
            else:
                suggestions["recommended_tools"] = stage_filtered_unused[:5]

        # 信心度提升建议
        if evaluation["confidence"] < 0.7:
            suggestions["confidence_boost"] = [
                "验证已获得的信息",
                "使用不同工具交叉验证",
                "检查逻辑一致性"
            ]

        return suggestions


# 全局策略管理器实例
strategy_manager = ReasoningStrategyManager()
