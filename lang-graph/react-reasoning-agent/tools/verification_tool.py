import re
from typing import Any, Dict, List

from langchain_core.tools import tool

from .tool_types import VerificationInput, VerificationOutput


@tool
def verify_answer(answer: str, question: str = "") -> Dict[str, Any]:
    """验证答案的合理性和正确性

    Args:
        answer: 要验证的答案
        question: 原始问题（可选，用于更好的验证）

    Returns:
        包含验证结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "question": str,
            "answer": str,
            "is_correct": bool,
            "confidence": float,
            "explanation": str
        }
    """

    try:
        if not answer.strip():
            return {
                "status": "error",
                "message": "答案不能为空",
                "question": question,
                "answer": "",
                "is_correct": False,
                "confidence": 0.0,
                "explanation": "答案为空，无法验证"
            }

        # 验证检查项
        checks = []
        positive_score = 0
        total_checks = 0

        # 1. 答案长度检查
        total_checks += 1
        if len(answer.strip()) < 5:
            checks.append("答案过短，可能不完整")
        else:
            checks.append("答案长度合适")
            positive_score += 1

        # 2. 答案结构检查
        total_checks += 1
        if "\n" in answer or len(answer) > 100:
            checks.append("答案包含详细信息")
            positive_score += 1
        else:
            checks.append("答案较简洁")

        # 3. 数字答案检查
        numbers = re.findall(r'-?\d+\.?\d*', answer)
        if numbers:
            total_checks += 1
            checks.append(f"发现数值: {numbers}")

            # 检查数值合理性
            reasonable = True
            for num in numbers:
                try:
                    val = float(num)
                    if val < -1000000 or val > 1000000:
                        reasonable = False
                        break
                except ValueError:
                    pass

            if reasonable:
                positive_score += 1
                checks.append("数值范围合理")
            else:
                checks.append("包含异常数值，请确认")

        # 4. 确定性检查
        total_checks += 1
        confident_words = ['是', '不是', '确定', '肯定', '一定', '必须', '绝对']
        uncertain_words = ['可能', '也许', '大概', '似乎', '或许', '估计', '推测']

        confident_count = sum(1 for word in confident_words if word in answer)
        uncertain_count = sum(1 for word in uncertain_words if word in answer)

        if confident_count > uncertain_count:
            checks.append("答案表达确定性较高")
            positive_score += 1
        elif uncertain_count > 0:
            checks.append("答案包含不确定表述")
        else:
            checks.append("答案语调中性")
            positive_score += 0.5

        # 5. 逻辑一致性检查
        total_checks += 1
        contradictory_patterns = [
            (['是', '正确'], ['不是', '错误', '不正确']),
            (['增加', '上升', '提高'], ['减少', '下降', '降低']),
            (['好', '优秀', '优点'], ['坏', '差', '缺点'])
        ]

        has_contradiction = False
        for positive, negative in contradictory_patterns:
            has_positive = any(word in answer for word in positive)
            has_negative = any(word in answer for word in negative)
            if has_positive and has_negative:
                has_contradiction = True
                break

        if not has_contradiction:
            checks.append("未发现明显的逻辑矛盾")
            positive_score += 1
        else:
            checks.append("答案包含可能矛盾的表述")

        # 6. 问题相关性检查
        if question:
            total_checks += 1
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())
            common_words = question_words & answer_words

            if len(common_words) >= 2:
                checks.append("答案与问题高度相关")
                positive_score += 1
            elif len(common_words) == 1:
                checks.append("答案与问题相关性一般")
                positive_score += 0.5
            else:
                checks.append("答案与问题相关性较低")

        # 计算信心度
        confidence = (positive_score /
                      total_checks) if total_checks > 0 else 0.0
        is_correct = confidence >= 0.6  # 60%以上认为正确

        # 生成解释
        explanation = f"验证检查项: {'; '.join(checks)}"

        return {
            "status": "success",
            "message": "答案验证完成",
            "question": question,
            "answer": answer,
            "is_correct": is_correct,
            "confidence": round(confidence, 2),
            "explanation": explanation
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"验证失败: {str(e)}",
            "question": question,
            "answer": answer,
            "is_correct": False,
            "confidence": 0.0,
            "explanation": ""
        }
