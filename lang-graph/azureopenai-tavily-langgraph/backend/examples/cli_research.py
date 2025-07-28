import argparse
import logging
import os
import sys

from agent.graph import graph
from agent.state import OverallState
from langchain_core.messages import HumanMessage

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def check_env():
    """检查必需的环境变量。"""
    required_azure_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
    ]
    missing = [var for var in required_azure_vars if not os.getenv(var)]
    if missing:
        print(f"[环境变量缺失] 缺少: {', '.join(missing)}")
        exit(1)
    # Tavily 可选
    if not os.getenv("TAVILY_API_KEY"):
        print("[警告] 未配置 TAVILY_API_KEY，部分搜索功能将不可用。")


def main() -> None:
    """从命令行运行研究代理。"""
    check_env()
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(
        description="运行 LangGraph 研究代理")
    parser.add_argument("question", nargs="?", default=None,
                        help="研究问题")
    parser.add_argument(
        "--initial-queries",
        type=int,
        default=3,
        help="初始搜索查询数量",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=2,
        help="最大研究循环数",
    )
    parser.add_argument(
        "--reasoning-model",
        default="gpt-4o-mini",  # 默认用 AzureOpenAI 部署名
        help="最终答案的模型",
    )
    args = parser.parse_args()

    # 如果没有参数，自动加上默认问题
    if len(sys.argv) == 1:
        sys.argv += ["人工智能在医疗诊断中的应用"]
    question = args.question or "人工智能在医疗诊断中的应用"

    logger.info(f"\n🔬 [deepresearcher] 研究主题: {question}")
    logger.info(
        f"参数: initial_queries={args.initial_queries}, max_loops={args.max_loops}, model={args.reasoning_model}")

    state: OverallState = {
        "messages": [HumanMessage(content=question)],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "initial_search_query_count": args.initial_queries,
        "max_research_loops": args.max_loops,
        "research_loop_count": 0,
        "reasoning_model": args.reasoning_model,
    }

    # 逐步打印每轮循环的详细日志
    result = None
    try:
        for step in graph.stream(state):
            loop = step.get("research_loop_count", 0)
            if "search_query" in step and loop > 0:
                logger.info(f"\n{'='*20} 研究循环 #{loop} {'='*20}")
            if "search_query" in step:
                queries = step["search_query"]
                if isinstance(queries, list):
                    logger.info(
                        f"🌐 [deepresearcher] 执行网络搜索: {', '.join(map(str, queries))}")
                else:
                    logger.info(f"🌐 [deepresearcher] 执行网络搜索: {queries}")
            if "web_research_result" in step:
                logger.info(
                    f"🌐 [deepresearcher] 搜索结果摘要: {step['web_research_result'][0][:100]}... 共{len(step.get('sources_gathered', []))}条")
            if "sources_gathered" in step and step["sources_gathered"]:
                logger.info("🌐 [deepresearcher] 本轮详细搜索结果：")
                for idx, src in enumerate(step["sources_gathered"], 1):
                    title = src.get("label", "")
                    url = src.get("value", "")
                    content = src.get("content", "")[:100]
                    logger.info(f"  {idx}. [{title}]({url}) {content}")
            if "is_sufficient" in step:
                logger.info(
                    f"🤔 [deepresearcher] 反思: 信息充分={step['is_sufficient']} | 知识缺口={step.get('knowledge_gap', '')} | 后续查询={step.get('follow_up_queries', [])}")
                if step["is_sufficient"]:
                    logger.info("[deepresearcher] 信息已充分，准备生成最终答案。\n")
                else:
                    logger.info("[deepresearcher] 信息不充分，继续研究下一轮。\n")
            if "messages" in step and step["messages"]:
                logger.info("📝 [deepresearcher] 生成最终答案...\n")
                result = step
    except Exception as e:
        logger.error(f"[deepresearcher] 研究流程异常: {e}")
        raise

    if result:
        messages = result.get("messages", [])
        if messages:
            print(
                "\n================= [deepresearcher] 最终答案 =================\n")
            print(messages[-1].content)
            print("\n===========================================================\n")
        else:
            logger.warning("[deepresearcher] 未生成最终答案。")
    else:
        logger.warning("[deepresearcher] 研究流程未获得有效结果。")


if __name__ == "__main__":
    main()
