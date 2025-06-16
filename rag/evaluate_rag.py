"""
RAG系统评估工具
用于测试和评估RAG系统的性能和准确性
"""

import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

from quick_start import create_quick_rag

# 加载环境变量
load_dotenv()

class RAGEvaluator:
    """RAG系统评估器"""
    
    def __init__(self):
        """初始化评估器"""
        self.test_questions = [
            {
                "question": "什么是人工智能？",
                "expected_keywords": ["计算机科学", "模拟", "人类智能", "算法"]
            },
            {
                "question": "机器学习有哪些主要类型？",
                "expected_keywords": ["监督学习", "无监督学习", "强化学习"]
            },
            {
                "question": "深度学习的优势是什么？",
                "expected_keywords": ["神经网络", "复杂模式", "图像识别", "语音识别"]
            },
            {
                "question": "RAG技术是什么？",
                "expected_keywords": ["检索", "生成", "知识截断", "幻觉问题"]
            },
            {
                "question": "大语言模型有什么局限性？",
                "expected_keywords": ["知识截断", "幻觉问题", "偏见", "计算成本"]
            }
        ]
    
    def evaluate_answer_quality(self, question: str, answer: str, expected_keywords: List[str]) -> Dict[str, Any]:
        """
        评估回答质量
        
        Args:
            question: 问题
            answer: 生成的回答
            expected_keywords: 期望的关键词
            
        Returns:
            评估结果字典
        """
        answer_lower = answer.lower()
        
        # 检查关键词覆盖率
        found_keywords = []
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                found_keywords.append(keyword)
        
        keyword_coverage = len(found_keywords) / len(expected_keywords)
        
        # 评估回答长度
        answer_length = len(answer)
        length_score = min(answer_length / 200, 1.0)  # 期望回答长度至少200字符
        
        # 检查回答是否包含"不知道"等表达
        uncertainty_phrases = ["不知道", "不确定", "无法确定", "不清楚"]
        has_uncertainty = any(phrase in answer for phrase in uncertainty_phrases)
        
        # 综合评分
        overall_score = (keyword_coverage * 0.6 + length_score * 0.3 + (0 if has_uncertainty else 0.1))
        
        return {
            "question": question,
            "answer": answer,
            "keyword_coverage": keyword_coverage,
            "found_keywords": found_keywords,
            "missing_keywords": [kw for kw in expected_keywords if kw not in found_keywords],
            "answer_length": answer_length,
            "length_score": length_score,
            "has_uncertainty": has_uncertainty,
            "overall_score": overall_score
        }
    
    def run_evaluation(self) -> Dict[str, Any]:
        """
        运行完整评估
        
        Returns:
            评估结果
        """
        print("🔍 开始RAG系统评估...")
        print("=" * 50)
        
        try:
            # 创建RAG系统
            print("正在初始化RAG系统...")
            rag_chain, retriever = create_quick_rag()
            
            results = []
            total_time = 0
            
            for i, test_case in enumerate(self.test_questions, 1):
                question = test_case["question"]
                expected_keywords = test_case["expected_keywords"]
                
                print(f"\n📝 测试问题 {i}: {question}")
                print("-" * 30)
                
                # 记录响应时间
                start_time = time.time()
                
                try:
                    # 获取相关文档
                    relevant_docs = retriever.get_relevant_documents(question)
                    print(f"检索到 {len(relevant_docs)} 个相关文档")
                    
                    # 生成回答
                    answer = rag_chain.invoke(question)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    total_time += response_time
                    
                    # 评估回答质量
                    evaluation = self.evaluate_answer_quality(question, answer, expected_keywords)
                    evaluation["response_time"] = response_time
                    evaluation["num_retrieved_docs"] = len(relevant_docs)
                    
                    results.append(evaluation)
                    
                    # 显示结果
                    print(f"✅ 回答生成完成 (用时: {response_time:.2f}秒)")
                    print(f"关键词覆盖率: {evaluation['keyword_coverage']:.2%}")
                    print(f"找到的关键词: {evaluation['found_keywords']}")
                    if evaluation['missing_keywords']:
                        print(f"遗漏的关键词: {evaluation['missing_keywords']}")
                    print(f"综合评分: {evaluation['overall_score']:.2f}/1.0")
                    
                except Exception as e:
                    print(f"❌ 处理问题时出错: {e}")
                    continue
            
            # 计算总体统计
            if results:
                avg_score = sum(r['overall_score'] for r in results) / len(results)
                avg_coverage = sum(r['keyword_coverage'] for r in results) / len(results)
                avg_response_time = total_time / len(results)
                
                summary = {
                    "total_questions": len(self.test_questions),
                    "successful_responses": len(results),
                    "success_rate": len(results) / len(self.test_questions),
                    "average_score": avg_score,
                    "average_keyword_coverage": avg_coverage,
                    "average_response_time": avg_response_time,
                    "total_time": total_time,
                    "detailed_results": results
                }
                
                self.print_summary(summary)
                return summary
            else:
                print("❌ 没有成功的测试结果")
                return {"error": "No successful test results"}
                
        except Exception as e:
            print(f"❌ 评估过程中出错: {e}")
            return {"error": str(e)}
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """打印评估摘要"""
        print("\n" + "=" * 60)
        print("📊 评估摘要")
        print("=" * 60)
        
        print(f"总问题数: {summary['total_questions']}")
        print(f"成功回答数: {summary['successful_responses']}")
        print(f"成功率: {summary['success_rate']:.2%}")
        print(f"平均评分: {summary['average_score']:.2f}/1.0")
        print(f"平均关键词覆盖率: {summary['average_keyword_coverage']:.2%}")
        print(f"平均响应时间: {summary['average_response_time']:.2f}秒")
        print(f"总用时: {summary['total_time']:.2f}秒")
        
        # 性能等级评定
        avg_score = summary['average_score']
        if avg_score >= 0.8:
            grade = "🏆 优秀"
        elif avg_score >= 0.6:
            grade = "👍 良好"
        elif avg_score >= 0.4:
            grade = "⚠️ 一般"
        else:
            grade = "❌ 需要改进"
        
        print(f"系统评级: {grade}")
        
        # 改进建议
        print("\n💡 改进建议:")
        if summary['average_keyword_coverage'] < 0.7:
            print("- 考虑优化检索策略，提高关键信息覆盖率")
        if summary['average_response_time'] > 10:
            print("- 响应时间较长，考虑优化模型配置或使用缓存")
        if summary['success_rate'] < 1.0:
            print("- 存在失败的查询，检查错误处理和系统稳定性")
    
    def run_interactive_test(self) -> None:
        """运行交互式测试"""
        print("🎯 交互式RAG测试")
        print("=" * 30)
        
        try:
            rag_chain, retriever = create_quick_rag()
            
            print("RAG系统已准备就绪！")
            print("输入问题进行测试，输入 'quit' 退出")
            
            while True:
                question = input("\n请输入测试问题: ").strip()
                
                if question.lower() in ['quit', 'exit', '退出']:
                    print("测试结束！")
                    break
                
                if not question:
                    continue
                
                start_time = time.time()
                
                try:
                    # 检索相关文档
                    relevant_docs = retriever.get_relevant_documents(question)
                    
                    # 生成回答
                    answer = rag_chain.invoke(question)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    print(f"\n📋 测试结果:")
                    print(f"检索文档数: {len(relevant_docs)}")
                    print(f"响应时间: {response_time:.2f}秒")
                    print(f"回答: {answer}")
                    
                    # 显示检索到的文档片段
                    if relevant_docs:
                        print(f"\n🔍 相关文档片段:")
                        for i, doc in enumerate(relevant_docs[:2], 1):  # 只显示前2个
                            print(f"[{i}] {doc.page_content[:100]}...")
                    
                except Exception as e:
                    print(f"❌ 处理问题时出错: {e}")
        
        except Exception as e:
            print(f"❌ 初始化测试环境失败: {e}")


def main():
    """主函数"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置OPENAI_API_KEY环境变量")
        return
    
    evaluator = RAGEvaluator()
    
    while True:
        print("\n🚀 RAG系统评估工具")
        print("=" * 30)
        print("1. 运行自动评估")
        print("2. 交互式测试")
        print("3. 退出")
        
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == "1":
            evaluator.run_evaluation()
        elif choice == "2":
            evaluator.run_interactive_test()
        elif choice == "3":
            print("再见！")
            break
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    main() 