import logging
import os
import sys
from typing import Any, Dict

from agent.configuration import Configuration
from agent.graph import generate_query
from agent.state import OverallState
from agent.tools_and_schemas import SearchQueryList
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

# 添加 src 目录到路径
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


# 设置日志
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


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
        return False
    return True


def test_generate_query():
    """测试 generate_query 函数"""
    if not check_env():
        return

    # 创建测试状态
    test_state: OverallState = {
        "messages": [HumanMessage(content="人工智能在医疗诊断中的应用")],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "initial_search_query_count": 3,
        "max_research_loops": 2,
        "research_loop_count": 0,
        "reasoning_model": "gpt-4o-mini",
    }

    # 创建配置
    config: RunnableConfig = {
        "configurable": {
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "azure_openai_deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            "tavily_api_key": os.getenv("TAVILY_API_KEY"),
            "max_research_loops": 2,
            "reflection_model": "gpt-4o-mini",
            "answer_model": "gpt-4o-mini",
        }
    }

    try:
        logger.info("🧪 开始测试 generate_query 函数...")
        logger.info(f"测试问题: {test_state['messages'][0].content}")
        logger.info(f"初始查询数量: {test_state['initial_search_query_count']}")

        # 调用 generate_query 函数
        result = generate_query(test_state, config)

        # 检查结果
        logger.info("✅ generate_query 函数执行成功!")
        logger.info(f"生成的查询: {result.get('search_query', [])}")

        # 验证结果格式
        if 'search_query' in result:
            queries = result['search_query']
            if isinstance(queries, list) and len(queries) > 0:
                logger.info(f"✅ 成功生成 {len(queries)} 个搜索查询")
                for i, query in enumerate(queries, 1):
                    logger.info(f"  查询 {i}: {query}")
            else:
                logger.warning("⚠️ 生成的查询格式不正确或为空")
        else:
            logger.error("❌ 结果中缺少 'search_query' 字段")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        raise


def test_different_topics():
    """测试不同主题的查询生成"""
    if not check_env():
        return

    test_topics = [
        "量子计算的发展现状",
        "可再生能源技术的最新进展",
        "机器学习在金融领域的应用",
        "区块链技术的商业应用案例"
    ]

    config: RunnableConfig = {
        "configurable": {
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "azure_openai_deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            "tavily_api_key": os.getenv("TAVILY_API_KEY"),
            "max_research_loops": 2,
            "reflection_model": "gpt-4o-mini",
            "answer_model": "gpt-4o-mini",
        }
    }

    for topic in test_topics:
        logger.info(f"\n{'='*50}")
        logger.info(f"测试主题: {topic}")
        logger.info(f"{'='*50}")

        test_state: OverallState = {
            "messages": [HumanMessage(content=topic)],
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": 2,  # 减少查询数量以加快测试
            "max_research_loops": 2,
            "research_loop_count": 0,
            "reasoning_model": "gpt-4o-mini",
        }

        try:
            result = generate_query(test_state, config)
            queries = result.get('search_query', [])
            logger.info(f"✅ 为主题 '{topic}' 生成了 {len(queries)} 个查询")
            for i, query in enumerate(queries, 1):
                logger.info(f"  查询 {i}: {query}")
        except Exception as e:
            logger.error(f"❌ 主题 '{topic}' 测试失败: {e}")


if __name__ == "__main__":
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    print("🧪 generate_query 函数测试")
    print("=" * 50)

    # 运行基本测试
    test_generate_query()

    print("\n" + "=" * 50)
    print("🧪 多主题测试")
    print("=" * 50)

    # 运行多主题测试
    test_different_topics()

    print("\n✅ 所有测试完成!")


def test_multilingual_queries():
    """测试多语言查询生成"""
    if not check_env():
        return

    # 多语言测试用例
    multilingual_topics = [
        # 中文测试用例
        "人工智能在医疗诊断中的应用",
        "量子计算的发展现状",
        "可再生能源技术的最新进展",
        # 英文测试用例
        "Artificial intelligence applications in medical diagnosis",
        "Quantum computing development status",
        "Latest advances in renewable energy technology",
        # 混合语言测试用例
        "AI在医疗诊断中的应用",
        "Quantum computing 发展现状",
        "Renewable energy 技术进展"
    ]

    config: RunnableConfig = {
        "configurable": {
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "azure_openai_deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            "tavily_api_key": os.getenv("TAVILY_API_KEY"),
            "max_research_loops": 2,
            "reflection_model": "gpt-4o-mini",
            "answer_model": "gpt-4o-mini",
        }
    }

    logger.info(f"\n{'='*60}")
    logger.info("🌍 多语言查询生成测试")
    logger.info(f"{'='*60}")

    for topic in multilingual_topics:
        logger.info(f"\n📝 测试主题: {topic}")
        logger.info("-" * 40)

        test_state: OverallState = {
            "messages": [HumanMessage(content=topic)],
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": 2,  # 减少查询数量以加快测试
            "max_research_loops": 2,
            "research_loop_count": 0,
            "reasoning_model": "gpt-4o-mini",
        }

        try:
            result = generate_query(test_state, config)
            queries = result.get('search_query', [])
            logger.info(f"✅ 生成了 {len(queries)} 个查询")

            # 分析查询语言
            chinese_count = 0
            english_count = 0
            for query in queries:
                # 简单的中文检测（包含中文字符）
                if any('\u4e00' <= char <= '\u9fff' for char in query):
                    chinese_count += 1
                else:
                    english_count += 1

            logger.info(
                f"📊 语言分布: 中文查询 {chinese_count} 个, 英文查询 {english_count} 个")

            for i, query in enumerate(queries, 1):
                logger.info(f"  查询 {i}: {query}")

        except Exception as e:
            logger.error(f"❌ 主题 '{topic}' 测试失败: {e}")


if __name__ == "__main__":
    print("🧪 generate_query 函数测试")
    print("=" * 50)

    # 运行基本测试
    test_generate_query()

    print("\n" + "=" * 50)
    print("🧪 多主题测试")
    print("=" * 50)

    # 运行多主题测试
    test_different_topics()

    # 运行多语言测试
    test_multilingual_queries()

    print("\n✅ 所有测试完成!")
