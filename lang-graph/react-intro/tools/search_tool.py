from langchain_core.tools import tool

@tool
def search_information(query: str) -> str:
    """搜索相关信息
    
    Args:
        query: 搜索查询字符串
    
    Returns:
        搜索结果信息
    """
    
    # 模拟搜索结果的知识库
    knowledge_base = {
        "python": """
Python是一种高级编程语言，具有以下特点：
- 简洁易读的语法
- 强大的标准库
- 跨平台支持
- 广泛的第三方库生态
- 适用于Web开发、数据科学、AI等领域
        """,
        
        "机器学习": """
机器学习是人工智能的一个分支，主要概念包括：
- 监督学习：使用标记数据训练模型
- 无监督学习：从未标记数据中发现模式
- 强化学习：通过奖励机制学习最优策略
- 常用算法：决策树、神经网络、支持向量机等
        """,
        
        "langgraph": """
LangGraph是一个用于构建多智能体应用的框架：
- 基于有向图的状态管理
- 支持条件边和循环
- 与LangChain集成
- 适用于复杂的工作流编排
- 支持并行和串行执行
        """,
        
        "react reasoning": """
ReAct (Reasoning and Acting) 是一种大模型推理方法：
- 交替进行推理(Reasoning)和行动(Acting)
- Think -> Act -> Observe 的循环模式
- 通过工具调用获取外部信息
- 逐步分解复杂问题
- 提高推理的准确性和可解释性
        """,
        
        "天气": """
今天的天气信息：
- 北京：晴天，气温15-25℃，微风
- 上海：多云，气温18-26℃，东南风3-4级
- 广州：小雨，气温22-28℃，南风2-3级
- 深圳：阴天，气温21-27℃，东风2级
        """,
        
        "数学公式": """
常用数学公式：
- 圆面积：S = πr²
- 球体积：V = (4/3)πr³
- 二次方程：ax² + bx + c = 0，解为 x = (-b ± √(b²-4ac)) / 2a
- 欧拉公式：e^(iπ) + 1 = 0
- 勾股定理：a² + b² = c²
        """
    }
    
    # 将查询转换为小写进行匹配
    query_lower = query.lower()
    
    # 查找匹配的知识
    for key, value in knowledge_base.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            return f"搜索查询: {query}\n\n找到相关信息:\n{value}"
    
    # 如果没有找到直接匹配，进行模糊搜索
    partial_matches = []
    for key, value in knowledge_base.items():
        # 检查查询中的关键词是否在知识库条目中
        query_words = query_lower.split()
        key_words = key.lower().split()
        if any(qword in key or any(qword in kword for kword in key_words) for qword in query_words):
            partial_matches.append((key, value))
    
    if partial_matches:
        result = f"搜索查询: {query}\n\n找到部分匹配的信息:\n"
        for key, value in partial_matches[:2]:  # 最多返回2个匹配
            result += f"\n=== {key} ===\n{value}\n"
        return result
    
    # 如果完全没有找到，返回通用搜索结果
    return f"""
搜索查询: {query}

未找到具体匹配的信息，但我可以搜索以下主题：
- Python编程
- 机器学习
- LangGraph框架  
- ReAct推理方法
- 天气信息
- 数学公式

请尝试更具体的搜索词，或者询问这些主题相关的问题。
    """ 