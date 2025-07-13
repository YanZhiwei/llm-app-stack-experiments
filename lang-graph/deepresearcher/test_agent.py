#!/usr/bin/env python3
"""
测试Research Agent
"""

import logging

from agent import run_research, stream_research

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_research():
    """测试基本研究功能"""
    print("🧪 测试基本研究功能...")

    topic = "量子计算的发展"
    result = run_research(topic)

    print(f"✅ 研究完成")
    print(f"主题: {result['topic']}")
    print(f"查询数量: {len(result.get('queries', []))}")
    print(f"结果数量: {result.get('results_count', 0)}")
    print(f"答案长度: {len(result.get('answer', ''))} 字符")

    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return False

    return True


def test_stream_research():
    """测试流式研究功能"""
    print("\n🧪 测试流式研究功能...")

    topic = "机器学习在金融中的应用"
    step_count = 0

    for step in stream_research(topic):
        step_count += 1
        print(f"步骤 {step_count}: {type(step).__name__}")

    print(f"✅ 流式研究完成，共 {step_count} 个步骤")
    return True


def main():
    """主测试函数"""
    print("🔬 Research Agent 测试")
    print("="*50)

    # 测试基本研究
    success1 = test_basic_research()

    # 测试流式研究
    success2 = test_stream_research()

    print("\n" + "="*50)
    print("📊 测试结果:")
    print(f"基本研究: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"流式研究: {'✅ 通过' if success2 else '❌ 失败'}")

    if success1 and success2:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")


if __name__ == "__main__":
    main()
