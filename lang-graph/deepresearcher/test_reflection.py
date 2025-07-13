"""
测试Reflection机制
"""

import logging

from agent import run_research

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_reflection_mechanism():
    """测试reflection机制"""
    print("🧪 测试DeepResearcher的Reflection机制")
    print("=" * 60)

    # 测试一个需要多轮研究的话题
    topic = "量子计算在药物发现中的应用前景"

    print(f"研究主题: {topic}")
    print("预期行为: 系统应该进行多轮搜索和反思")
    print("-" * 60)

    try:
        result = run_research(topic)

        print("\n📊 研究统计:")
        print(f"  研究循环次数: {result['research_loops']}")
        print(f"  研究质量评分: {result['quality_score']:.2f}")
        print(f"  信息是否充分: {'是' if result['is_sufficient'] else '否'}")
        print(f"  搜索查询数量: {len(result['queries'])}")
        print(f"  搜索结果数量: {result['results_count']}")

        print("\n🔍 搜索查询:")
        for i, query in enumerate(result['queries'], 1):
            print(f"  {i}. {query}")

        print("\n📝 最终答案:")
        print(result['answer'])

        # 分析reflection效果
        print("\n🤔 Reflection分析:")
        if result['research_loops'] > 1:
            print("✅ 系统成功进行了多轮研究，体现了reflection机制")
        else:
            print("⚠️ 系统只进行了一轮研究，可能需要调整reflection阈值")

        if result['quality_score'] > 0.7:
            print("✅ 研究质量评分较高，reflection机制有效")
        else:
            print("⚠️ 研究质量评分较低，可能需要优化reflection逻辑")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_reflection_mechanism()
