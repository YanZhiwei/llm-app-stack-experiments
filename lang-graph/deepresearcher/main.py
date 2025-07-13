#!/usr/bin/env python3
"""
Research Agent 主程序
"""

import logging
import sys
from typing import List

from agent import run_research, stream_research

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def select_research_topic() -> str:
    """选择研究主题"""
    demo_questions = [
        "人工智能在医疗诊断中的应用",
        "区块链技术在供应链管理中的创新",
        "可再生能源技术的最新发展",
        "量子计算在密码学中的影响",
        "自动驾驶汽车的安全性和法规",
        "机器学习在金融风控中的应用",
        "5G技术在物联网中的发展",
        "基因编辑技术的伦理问题",
        "虚拟现实在教育领域的应用",
        "可持续发展与绿色技术"
    ]

    print("\n🎯 请选择研究主题:")
    for i, question in enumerate(demo_questions, 1):
        print(f"{i:2d}. {question}")
    print(f"{len(demo_questions)+1:2d}. 自定义问题")

    while True:
        choice = input(f"\n请选择问题 (1-{len(demo_questions)+1}): ").strip()

        if choice == str(len(demo_questions)+1):
            # 自定义问题
            research_topic = input("请输入您的研究主题: ").strip()
            if not research_topic:
                print("❌ 研究主题不能为空")
                continue
            return research_topic
        else:
            # 预定义问题
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(demo_questions):
                    return demo_questions[idx]
                else:
                    print("❌ 无效的选择")
            except ValueError:
                print("❌ 请输入有效的数字")


def display_result(result: dict):
    """显示研究结果"""
    print("\n" + "="*60)
    print("📋 研究结果")
    print("="*60)
    print(f"主题: {result['topic']}")

    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return

    print(f"查询数量: {len(result.get('queries', []))}")
    print(f"结果数量: {result.get('results_count', 0)}")

    if result.get('queries'):
        print("\n🔍 搜索查询:")
        for i, query in enumerate(result['queries'], 1):
            print(f"  {i}. {query}")

    print("\n📝 答案:")
    print(result.get('answer', '无答案'))
    print("="*60)


def main():
    """主函数"""
    print("🔬 Research Agent - 基于LangGraph的研究代理")
    print("="*60)

    try:
        # 选择研究主题
        research_topic = select_research_topic()

        # 运行研究
        result = run_research(research_topic)

        # 显示结果
        display_result(result)

    except KeyboardInterrupt:
        print("\n⏹️  程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        logger.exception("程序执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
