from langchain_core.tools import tool

@tool
def verify_answer(answer: str, problem: str = "") -> str:
    """验证答案的合理性和正确性
    
    Args:
        answer: 要验证的答案
        problem: 原始问题（可选，用于更好的验证）
    
    Returns:
        验证结果和建议
    """
    
    verification_result = f"答案验证报告\n{'='*30}\n\n"
    verification_result += f"待验证答案: {answer}\n"
    
    if problem:
        verification_result += f"原始问题: {problem}\n"
    
    verification_result += f"\n验证检查项:\n"
    
    # 基本检查
    checks = []
    
    # 1. 答案长度检查
    if len(answer.strip()) == 0:
        checks.append("❌ 答案为空")
    elif len(answer.strip()) < 5:
        checks.append("⚠️ 答案过短，可能不完整")
    else:
        checks.append("✅ 答案长度合适")
    
    # 2. 答案结构检查
    if "\n" in answer or len(answer) > 100:
        checks.append("✅ 答案包含详细信息")
    else:
        checks.append("⚠️ 答案较简洁，可能需要更多细节")
    
    # 3. 数字答案检查
    import re
    numbers = re.findall(r'-?\d+\.?\d*', answer)
    if numbers:
        checks.append(f"✅ 发现数值: {numbers}")
        
        # 检查数值合理性
        for num in numbers:
            try:
                val = float(num)
                if val < 0:
                    checks.append(f"⚠️ 包含负数 {val}，请确认合理性")
                elif val > 1000000:
                    checks.append(f"⚠️ 包含大数 {val}，请确认合理性")
            except ValueError:
                pass
    
    # 4. 关键词检查
    confident_words = ['是', '不是', '确定', '肯定', '一定', '必须', '绝对']
    uncertain_words = ['可能', '也许', '大概', '似乎', '或许', '估计', '推测']
    
    confident_count = sum(1 for word in confident_words if word in answer)
    uncertain_count = sum(1 for word in uncertain_words if word in answer)
    
    if confident_count > uncertain_count:
        checks.append("✅ 答案表达确定性较高")
    elif uncertain_count > 0:
        checks.append("⚠️ 答案包含不确定表述，可能需要进一步验证")
    else:
        checks.append("ℹ️ 答案语调中性")
    
    # 5. 逻辑一致性检查
    contradictory_patterns = [
        (['是', '正确'], ['不是', '错误', '不正确']),
        (['增加', '上升', '提高'], ['减少', '下降', '降低']),
        (['好', '优秀', '优点'], ['坏', '差', '缺点'])
    ]
    
    for positive, negative in contradictory_patterns:
        has_positive = any(word in answer for word in positive)
        has_negative = any(word in answer for word in negative)
        if has_positive and has_negative:
            checks.append("⚠️ 答案包含可能矛盾的表述，请检查逻辑一致性")
            break
    else:
        checks.append("✅ 未发现明显的逻辑矛盾")
    
    # 6. 问题相关性检查
    if problem:
        problem_words = set(problem.lower().split())
        answer_words = set(answer.lower().split())
        common_words = problem_words & answer_words
        
        if len(common_words) >= 2:
            checks.append("✅ 答案与问题高度相关")
        elif len(common_words) == 1:
            checks.append("⚠️ 答案与问题相关性一般")
        else:
            checks.append("❌ 答案与问题相关性较低")
    
    # 添加检查结果
    for check in checks:
        verification_result += f"  {check}\n"
    
    # 计算总体评分
    positive_checks = len([c for c in checks if c.startswith("✅")])
    warning_checks = len([c for c in checks if c.startswith("⚠️")])
    negative_checks = len([c for c in checks if c.startswith("❌")])
    
    total_checks = positive_checks + warning_checks + negative_checks
    score = (positive_checks * 2 + warning_checks * 1 + negative_checks * 0) / (total_checks * 2) * 100
    
    verification_result += f"\n验证评分: {score:.1f}/100\n"
    
    # 提供建议
    verification_result += f"\n建议:\n"
    if score >= 80:
        verification_result += "✅ 答案质量良好，可以接受\n"
    elif score >= 60:
        verification_result += "⚠️ 答案基本可用，建议进一步改进\n"
        if warning_checks > 0:
            verification_result += "- 解决警告项以提高答案质量\n"
    else:
        verification_result += "❌ 答案质量较低，建议重新思考\n"
        verification_result += "- 检查答案的完整性和相关性\n"
        verification_result += "- 确保逻辑一致性\n"
        
    if negative_checks > 0:
        verification_result += "- 重点关注标记为❌的问题\n"
    
    return verification_result 