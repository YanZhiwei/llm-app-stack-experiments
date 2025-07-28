from typing import Any, Dict, List

from langchain_core.tools import tool




@tool
def search_information(query: str) -> Dict[str, Any]:
    """搜索相关信息

    Args:
        query: 搜索查询字符串

    Returns:
        包含搜索结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "query": str,
            "results": List[str],
            "source": str
        }
    """

    try:
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
        results = []

        # 查找匹配的知识
        for key, value in knowledge_base.items():
            if key in query_lower or any(word in query_lower for word in key.split()):
                results.append(f"=== {key} ===\n{value.strip()}")

        # 如果没有找到直接匹配，进行模糊搜索
        if not results:
            partial_matches = []
            for key, value in knowledge_base.items():
                # 检查查询中的关键词是否在知识库条目中
                query_words = query_lower.split()
                key_words = key.lower().split()
                if any(qword in key or any(qword in kword for kword in key_words) for qword in query_words):
                    partial_matches.append(
                        f"=== {key} (部分匹配) ===\n{value.strip()}")

            if partial_matches:
                results = partial_matches[:2]  # 最多返回2个匹配

        # 如果还是没有找到，返回可用主题
        if not results:
            available_topics = list(knowledge_base.keys())
            results = [f"未找到匹配内容，可搜索的主题：{', '.join(available_topics)}"]

        return {
            "status": "success",
            "message": f"搜索完成，找到{len(results)}个结果",
            "query": query,
            "results": results,
            "source": "内置知识库"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"搜索失败: {str(e)}",
            "query": query,
            "results": [],
            "source": ""
        }
