from typing import Any, Dict, List

from langchain_core.tools import tool

from .tool_types import ProblemAnalysisInput, ProblemAnalysisOutput


@tool
def analyze_problem(problem: str) -> Dict[str, Any]:
    """分析问题并提供推理建议

    Args:
        problem: 需要分析的问题描述

    Returns:
        包含问题分析结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "problem": str,
            "analysis": str,
            "steps": List[str],
            "complexity": "simple" | "medium" | "complex",
            "estimated_time": str
        }
    """

    try:
        if not problem.strip():
            return {
                "status": "error",
                "message": "问题描述不能为空",
                "problem": "",
                "analysis": "",
                "steps": [],
                "complexity": "simple",
                "estimated_time": "0分钟"
            }

        problem_lower = problem.lower()

        # 问题类型分析
        problem_types = {
            "数学": ["计算", "数学", "公式", "求解", "方程", "+", "-", "*", "/", "="],
            "搜索": ["查询", "搜索", "找", "什么是", "介绍", "了解"],
            "比较": ["比较", "区别", "不同", "相同", "对比", "哪个更好"],
            "解释": ["为什么", "怎么", "如何", "原理", "机制", "解释"],
            "推荐": ["推荐", "建议", "选择", "应该", "最好"],
            "步骤": ["步骤", "流程", "怎么做", "如何做", "方法"]
        }

        detected_types = []
        for ptype, keywords in problem_types.items():
            if any(keyword in problem_lower for keyword in keywords):
                detected_types.append(ptype)

        if not detected_types:
            detected_types = ["通用"]

        # 复杂度评估
        complexity_indicators = {
            "simple": ["是什么", "定义", "简单", "基本"],
            "complex": ["分析", "比较", "复杂", "深入", "详细", "综合", "多个", "全面"]
        }

        complexity = "medium"  # 默认中等复杂度

        for level, indicators in complexity_indicators.items():
            if any(indicator in problem_lower for indicator in indicators):
                complexity = level
                break

        # 估算时间
        time_estimates = {
            "simple": "1-2分钟",
            "medium": "3-5分钟",
            "complex": "5-10分钟"
        }

        estimated_time = time_estimates.get(complexity, "3-5分钟")

        # 生成分析结果
        analysis = f"检测到的问题类型: {', '.join(detected_types)}\n"
        analysis += f"复杂度: {complexity}\n"
        analysis += f"预计耗时: {estimated_time}"

        # 生成推理步骤
        steps = []

        if "数学" in detected_types:
            steps.extend([
                "识别数学概念和公式",
                "分解复杂计算为简单步骤",
                "使用计算工具验证结果",
                "检查答案合理性"
            ])

        if "搜索" in detected_types:
            steps.extend([
                "确定搜索关键词",
                "使用搜索工具获取信息",
                "整理和总结相关信息",
                "验证信息准确性"
            ])

        if "比较" in detected_types:
            steps.extend([
                "分别搜索每个对象的信息",
                "识别比较维度",
                "逐一对比特点",
                "总结优缺点"
            ])

        if "解释" in detected_types:
            steps.extend([
                "搜索基础概念",
                "分析因果关系",
                "使用类比和例子",
                "逐步深入解释"
            ])

        if "推荐" in detected_types:
            steps.extend([
                "了解需求和约束",
                "搜索可选方案",
                "评估各方案优劣",
                "基于标准做出推荐"
            ])

        if "步骤" in detected_types:
            steps.extend([
                "分解任务为子步骤",
                "确定步骤顺序",
                "识别关键节点",
                "提供具体指导"
            ])

        if "通用" in detected_types:
            steps.extend([
                "仔细理解问题需求",
                "分解为可处理的子问题",
                "逐步收集相关信息",
                "综合信息得出结论"
            ])

        # 去重并限制步骤数量
        unique_steps = []
        for step in steps:
            if step not in unique_steps:
                unique_steps.append(step)

        return {
            "status": "success",
            "message": "问题分析完成",
            "problem": problem,
            "analysis": analysis,
            "steps": unique_steps[:6],  # 最多6个步骤
            "complexity": complexity,
            "estimated_time": estimated_time
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"问题分析失败: {str(e)}",
            "problem": problem,
            "analysis": "",
            "steps": [],
            "complexity": "simple",
            "estimated_time": "0分钟"
        }
