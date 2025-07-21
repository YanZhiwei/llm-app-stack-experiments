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
        f"Missing Azure OpenAI environment variables: {', '.join(missing_vars)}")


load_dotenv()

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
    """LangGraph node that generates search queries based on the User's question.

    Uses Gemini 2.0 Flash to create an optimized search queries for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries
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
    """LangGraph node that performs web research using Tavily.

    Executes a web search using Tavily.

    Args:
        query: The search query to perform.
        api_key: The Tavily API key.

    Returns:
        A list of search results from Tavily.
    """
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


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> dict:
    # logger.info("🌐 [deepresearcher] 执行网络搜索...")  # 移除冗余日志
    configurable = Configuration.from_runnable_config(config)
    query = state["search_query"]
    all_results = []
    if configurable.tavily_api_key:
        import asyncio
        results = asyncio.run(tavily_search(
            query, configurable.tavily_api_key))
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
        "Tavily API Key is not set. Please set TAVILY_API_KEY environment variable.")


def reflection(state: OverallState, config: RunnableConfig) -> dict:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
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
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
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
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
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


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
