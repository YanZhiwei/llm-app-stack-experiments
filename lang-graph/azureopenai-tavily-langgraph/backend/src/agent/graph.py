import logging
import os

from agent.configuration import Configuration
from agent.prompts import (
    answer_instructions,
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
    web_searcher_instructions,
)
from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.tools_and_schemas import Reflection, SearchQueryList
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from tavily import TavilyClient

# 检查 AzureOpenAI 相关环境变量
required_azure_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
]
missing_vars = [var for var in required_azure_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f"缺少 Azure OpenAI 环境变量: {', '.join(missing_vars)}")


load_dotenv(encoding="utf-8")

# 移除所有与 GEMINI 相关的 import
# from google.genai import Client
# from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# Nodes


def create_llm_from_config(configurable):
    # 只支持 AzureOpenAI
    return AzureChatOpenAI(
        api_key=configurable.azure_openai_api_key,
        azure_endpoint=configurable.azure_openai_endpoint,
        api_version=configurable.azure_openai_api_version,
        azure_deployment=configurable.azure_openai_deployment,
        temperature=0.1,
        max_tokens=4000,
    )


def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """基于用户问题生成搜索查询的 LangGraph 节点。

    使用 Azure OpenAI 为网络研究创建优化的搜索查询，基于用户的问题。

    参数:
        state: 包含用户问题的当前图状态
        config: 可运行配置，包括 LLM 提供商设置

    返回:
        包含状态更新的字典，包括包含生成查询的 search_query 键
    """
    logger.info("🔍 [deepresearcher] 生成搜索查询...")
    configurable = Configuration.from_runnable_config(config)
    # 不再对 initial_search_query_count 赋值，只读取
    llm = create_llm_from_config(configurable)
    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    # 只允许 BaseModel，安全访问 query 字段
    queries = []
    if hasattr(result, "query"):
        queries = result.query
    elif isinstance(result, dict) and "query" in result:
        queries = result["query"]
    logger.info(f"✅ [deepresearcher] 生成查询: {queries}")
    return {"search_query": queries}


async def tavily_search(query, api_key):
    """使用 Tavily 执行网络研究的 LangGraph 节点。

    使用 Tavily 执行网络搜索。

    参数:
        query: 要执行的搜索查询。
        api_key: Tavily API 密钥。

    返回:
        来自 Tavily 的搜索结果列表。
    """
    import asyncio

    def _sync_tavily_search(query, api_key):
        client = TavilyClient(api_key=api_key)
        response = client.search(query, search_depth="basic", max_results=3)
        results = []
        for item in response.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', '')[:500]
            })
        return results

    # Run the blocking Tavily search in a separate thread
    return await asyncio.to_thread(_sync_tavily_search, query, api_key)


def continue_to_web_research(state: QueryGenerationState):
    """将搜索查询发送到网络研究节点的 LangGraph 节点。

    这用于生成 n 个网络研究节点，每个搜索查询一个。
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


async def web_research(state: WebSearchState, config: RunnableConfig) -> dict:
    # logger.info("🌐 [deepresearcher] 执行网络搜索...")  # 移除冗余日志
    configurable = Configuration.from_runnable_config(config)
    query = state["search_query"]
    all_results = []
    if configurable.tavily_api_key:
        results = await tavily_search(query, configurable.tavily_api_key)
        all_results.extend(results)
        sources_gathered = [
            {"label": r["title"], "short_url": r["url"],
                "value": r["url"], "content": r.get("content", "")}
            for r in results
        ]
        modified_text = "\n\n".join([
            f"{r['title']}\n{r['content']} [{r['title']}]({r['url']})" for r in results
        ])
        logger.info(f"✅ [deepresearcher] 获得 {len(all_results)} 个搜索结果")
        return {
            "search_query": [query],
            "web_research_result": [modified_text],
            "sources_gathered": sources_gathered,
        }
    raise ValueError(
        "未设置 Tavily API 密钥。请设置 TAVILY_API_KEY 环境变量。")


def reflection(state: OverallState, config: RunnableConfig) -> dict:
    """识别知识空白并生成潜在后续查询的 LangGraph 节点。

    分析当前摘要以识别需要进一步研究的领域，并生成潜在的后续查询。
    使用结构化输出来提取 JSON 格式的后续查询。

    参数:
        state: 包含运行摘要和研究主题的当前图状态
        config: 可运行配置，包括 LLM 提供商设置

    返回:
        包含状态更新的字典，包括包含生成的后续查询的 search_query 键
    """
    logger.info("🤔 [deepresearcher] 反思分析中...")
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get(
        "reasoning_model", configurable.reflection_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # init Reasoning Model
    llm = create_llm_from_config(configurable)
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)
    # 类型安全访问
    if hasattr(result, "is_sufficient"):
        is_sufficient = result.is_sufficient
        knowledge_gap = result.knowledge_gap
        follow_up_queries = result.follow_up_queries
    elif isinstance(result, dict):
        is_sufficient = result.get("is_sufficient", False)
        knowledge_gap = result.get("knowledge_gap", "")
        follow_up_queries = result.get("follow_up_queries", [])
    else:
        is_sufficient = False
        knowledge_gap = ""
        follow_up_queries = []
    logger.info(
        f"🔎 [deepresearcher] 反思结果: 信息充分={is_sufficient} | 知识缺口={knowledge_gap} | 后续查询={follow_up_queries}")
    return {
        "is_sufficient": is_sufficient,
        "knowledge_gap": knowledge_gap,
        "follow_up_queries": follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """确定研究流程中下一步的 LangGraph 路由函数。

    通过决定是继续收集信息还是基于配置的最大研究循环数来最终确定摘要，
    从而控制研究循环。

    参数:
        state: 包含研究循环计数的当前图状态
        config: 可运行配置，包括 max_research_loops 设置

    返回:
        指示下一个要访问的节点的字符串字面量（"web_research" 或 "finalize_summary"）
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig) -> dict:
    """最终确定研究摘要的 LangGraph 节点。

    通过去重和格式化源，然后将它们与运行摘要结合，
    创建结构良好的研究报告，并带有适当的引用。

    参数:
        state: 包含运行摘要和收集源的当前图状态

    返回:
        包含状态更新的字典，包括包含格式化最终摘要和源的 running_summary 键
    """
    logger.info("📝 [deepresearcher] 生成最终答案...")
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # init Reasoning Model, default to Gemini 2.5 Flash
    llm = create_llm_from_config(configurable)
    result = llm.invoke(formatted_prompt)

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result.content:
            result.content = result.content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)
    logger.info("✅ [deepresearcher] 答案生成完成")
    return {
        "messages": [AIMessage(content=result.content)],
        "sources_gathered": unique_sources,
    }


# 创建我们的代理图
builder = StateGraph(OverallState, config_schema=Configuration)

# 定义我们将在其间循环的节点
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# 将入口点设置为 `generate_query`
# 这意味着这个节点是第一个被调用的
builder.add_edge(START, "generate_query")
# 添加条件边以在并行分支中继续搜索查询
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# 反思网络研究
builder.add_edge("web_research", "reflection")
# 评估研究
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# 最终确定答案
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
