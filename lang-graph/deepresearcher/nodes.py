"""
Agent节点函数
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional

from langchain_core.runnables import RunnableConfig

from config import config
from state import AgentState

logger = logging.getLogger(__name__)


def generate_queries(state: AgentState, runnable_config: Optional[RunnableConfig] = None) -> AgentState:
    """生成搜索查询"""
    logger.info("🔍 生成搜索查询...")

    llm = config.create_llm()

    # 如果有后续查询，直接用
    if state.follow_up_queries:
        state.search_queries = state.follow_up_queries
        logger.info(f"🔄 使用反思生成的后续查询: {state.search_queries}")
        state.follow_up_queries = []  # 用完即清空，防止死循环
        return state

    prompt = f"""
    为以下研究主题生成3个高质量的搜索查询：

    研究主题：{state.research_topic}

    请生成3个不同的搜索查询，覆盖主题的不同方面。
    以JSON格式返回：{{"queries": ["查询1", "查询2", "查询3"]}}
    """

    try:
        response = llm.invoke(prompt)
        content = str(response.content)
        # 尝试解析JSON
        try:
            queries_json = json.loads(content)
            queries = queries_json.get("queries", [])
        except Exception:
            # 回退到原有解析
            lines = content.split('\n')
            queries = []
            for line in lines:
                if '"' in line and not line.strip().startswith('{') and not line.strip().startswith('}'):
                    query = line.split('"')[1] if '"' in line else line.strip()
                    if query and len(query) > 5:
                        queries.append(query)
        if not queries:
            queries = [
                f"{state.research_topic} 概述",
                f"{state.research_topic} 最新发展",
                f"{state.research_topic} 专家观点"
            ]
        state.search_queries = queries[:3]
        logger.info(
            f"✅ 生成了 {len(state.search_queries)} 个查询: {state.search_queries}")
    except Exception as e:
        logger.error(f"生成查询失败: {e}")
        state.search_queries = [
            f"{state.research_topic} 概述",
            f"{state.research_topic} 最新发展",
            f"{state.research_topic} 专家观点"
        ]
    return state


async def search_web(query: str) -> List[Dict]:
    """执行网络搜索"""
    try:
        if config.tavily_api_key:
            # 使用Tavily
            from tavily import TavilyClient
            client = TavilyClient(api_key=config.tavily_api_key)
            response = client.search(
                query, search_depth="basic", max_results=3)

            results = []
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'content': item.get('content', '')[:500]
                })
            return results
        else:
            # 使用DuckDuckGo
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            results = []
            for item in ddgs.text(query, max_results=3):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('href', ''),
                    'content': item.get('body', '')[:500]
                })
            return results
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return []


def web_research(state: AgentState, runnable_config: Optional[RunnableConfig] = None) -> AgentState:
    """执行网络研究"""
    logger.info("🌐 执行网络研究...")

    all_results = []

    for i, query in enumerate(state.search_queries):
        logger.info(f"搜索 {i+1}/{len(state.search_queries)}: {query}")

        try:
            # 同步执行异步搜索
            results = asyncio.run(search_web(query))
            all_results.extend(results)

        except Exception as e:
            logger.error(f"查询 '{query}' 搜索失败: {e}")
            continue

    # 如果是后续搜索，合并结果
    if state.research_loop_count > 0:
        state.search_results.extend(all_results)
        logger.info(f"✅ 合并搜索结果，总计 {len(state.search_results)} 个")
    else:
        state.search_results = all_results
        logger.info(f"✅ 获得 {len(state.search_results)} 个搜索结果")

    return state


def reflection(state: AgentState, runnable_config: Optional[RunnableConfig] = None) -> AgentState:
    """反思分析，驱动多轮深度研究"""
    logger.info("🤔 反思分析中...")
    state.research_loop_count += 1
    llm = config.create_llm()
    search_summary = ""
    for i, result in enumerate(state.search_results):
        search_summary += f"\n来源 {i+1}: {result.get('title', '')}\n{result.get('content', '')[:200]}...\n"
    prompt = f"""
    你是一个严谨的研究型AI。请基于以下搜索结果，评估对研究主题的信息是否充分，并给出下一步建议：
    研究主题：{state.research_topic}
    当前循环：{state.research_loop_count}/{state.max_research_loops}
    搜索结果摘要：{search_summary}
    请严格以JSON格式返回：
    {{
        "is_sufficient": true/false,  // 是否信息充分
        "knowledge_gap": "知识缺口描述，若信息充分可写'无'",
        "follow_up_queries": ["后续查询1", "后续查询2"], // 若is_sufficient为false，必须给出2个具体、针对知识缺口的后续查询
        "quality_score": 0.0-1.0, // 研究质量评分
        "reasoning": "评估理由"
    }}
    注意：如果is_sufficient为false，follow_up_queries不能为空，且必须与knowledge_gap紧密相关。
    """
    try:
        response = llm.invoke(prompt)
        content = str(response.content)
        logger.info(f"📝 反思原始输出: {content}")
        # 尝试解析JSON
        try:
            result = json.loads(content)
            state.is_sufficient = bool(result.get("is_sufficient", False))
            state.knowledge_gap = result.get("knowledge_gap", "")
            # 无论is_sufficient如何都赋值follow_up_queries
            state.follow_up_queries = result.get("follow_up_queries", [])
            state.research_quality_score = float(
                result.get("quality_score", 0.5))
            reasoning = result.get("reasoning", "")
        except Exception:
            # 回退到原有解析
            state.is_sufficient = "true" in content.lower() and "is_sufficient" in content
            state.knowledge_gap = ""
            state.follow_up_queries = []
            state.research_quality_score = 0.5
            reasoning = ""
        logger.info(
            f"🔎 反思结果: 信息充分={state.is_sufficient} | 知识缺口={state.knowledge_gap} | 后续查询={state.follow_up_queries} | 质量分={state.research_quality_score:.2f}")
        if reasoning:
            logger.info(f"🧠 反思理由: {reasoning}")
    except Exception as e:
        logger.error(f"反思分析失败: {e}")
        state.is_sufficient = False
        state.knowledge_gap = ""
        state.follow_up_queries = [
            f"{state.research_topic} 具体案例研究",
            f"{state.research_topic} 技术挑战和解决方案"
        ]
        state.research_quality_score = 0.5
    return state


def should_continue_research(state: AgentState) -> str:
    """决定是否继续研究"""
    # 如果信息充分，直接生成答案
    if state.is_sufficient:
        return "generate_answer"

    # 如果达到最大循环次数，生成答案
    if state.research_loop_count >= state.max_research_loops:
        logger.info(f"达到最大循环次数 ({state.max_research_loops})，生成最终答案")
        return "generate_answer"

    # 如果没有后续查询，生成答案
    if not state.follow_up_queries:
        logger.info("没有后续查询，生成最终答案")
        return "generate_answer"

    # 继续研究
    logger.info(
        f"继续研究 (循环 {state.research_loop_count}/{state.max_research_loops})")
    return "generate_queries"


def generate_answer(state: AgentState, runnable_config: Optional[RunnableConfig] = None) -> AgentState:
    """生成最终答案"""
    logger.info("📝 生成最终答案...")

    llm = config.create_llm()

    # 构建搜索结果文本
    search_text = ""
    for i, result in enumerate(state.search_results):
        search_text += f"\n\n来源 {i+1}:\n标题: {result.get('title', '')}\n内容: {result.get('content', '')}\n"

    prompt = f"""
    基于以下搜索结果，为研究主题生成一个全面的答案：
    
    研究主题：{state.research_topic}
    研究循环次数：{state.research_loop_count}
    研究质量评分：{state.research_quality_score:.2f}
    
    搜索结果：{search_text}
    
    请生成一个结构化的答案，包括：
    1. 概述
    2. 主要发现
    3. 关键要点
    4. 结论
    
    请确保答案准确、全面，并基于提供的搜索结果。
    """

    try:
        response = llm.invoke(prompt)
        state.final_answer = str(response.content)
        logger.info("✅ 答案生成完成")

    except Exception as e:
        logger.error(f"生成答案失败: {e}")
        state.final_answer = f"抱歉，无法为 '{state.research_topic}' 生成答案。请检查网络连接和API配置。"

    return state
