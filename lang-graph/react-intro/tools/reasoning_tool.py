from langchain_core.tools import tool

@tool
def analyze_problem(problem: str) -> str:
    """分析问题并提供推理建议
    
    Args:
        problem: 需要分析的问题描述
    
    Returns:
        问题分析结果和推理建议
    """
    
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
    
    # 根据问题类型提供分析
    analysis = f"问题分析: {problem}\n\n"
    analysis += f"检测到的问题类型: {', '.join(detected_types)}\n\n"
    
    # 提供推理策略
    strategies = {
        "数学": """
推理策略:
1. 识别数学概念和公式
2. 分解复杂计算为简单步骤
3. 使用计算工具验证结果
4. 检查答案合理性
        """,
        
        "搜索": """
推理策略:
1. 确定搜索关键词
2. 使用搜索工具获取信息
3. 整理和总结相关信息
4. 验证信息准确性
        """,
        
        "比较": """
推理策略:
1. 分别搜索每个对象的信息
2. 识别比较维度
3. 逐一对比特点
4. 总结优缺点
        """,
        
        "解释": """
推理策略:
1. 搜索基础概念
2. 分析因果关系
3. 使用类比和例子
4. 逐步深入解释
        """,
        
        "推荐": """
推理策略:
1. 了解需求和约束
2. 搜索可选方案
3. 评估各方案优劣
4. 基于标准做出推荐
        """,
        
        "步骤": """
推理策略:
1. 分解任务为子步骤
2. 确定步骤顺序
3. 识别关键节点
4. 提供具体指导
        """,
        
        "通用": """
推理策略:
1. 仔细理解问题需求
2. 分解为可处理的子问题
3. 逐步收集相关信息
4. 综合信息得出结论
        """
    }
    
    # 添加相应的策略建议
    for ptype in detected_types:
        if ptype in strategies:
            analysis += f"\n=== {ptype}问题 ===\n{strategies[ptype]}"
    
    # 添加具体的下一步建议
    analysis += f"\n\n推荐的下一步行动:\n"
    
    if "数学" in detected_types:
        analysis += "- 使用calculate_math工具进行计算\n"
    
    if any(t in detected_types for t in ["搜索", "比较", "解释"]):
        analysis += "- 使用search_information工具搜索相关信息\n"
    
    analysis += "- 使用store_memory工具保存重要信息\n"
    analysis += "- 使用verify_answer工具验证最终答案\n"
    
    return analysis 