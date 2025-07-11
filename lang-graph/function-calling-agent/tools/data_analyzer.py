"""
数据分析工具 - 分析数据并提供统计信息
"""

import json

from langchain_core.tools import tool


@tool
def analyze_data(data: str) -> str:
    """分析数据并提供统计信息"""
    try:
        # 尝试解析为JSON数组
        if data.startswith('[') and data.endswith(']'):
            numbers = json.loads(data)
            if all(isinstance(x, (int, float)) for x in numbers):
                avg = sum(numbers) / len(numbers)
                return f"数据分析结果:\n数量: {len(numbers)}\n平均值: {avg:.2f}\n最大值: {max(numbers)}\n最小值: {min(numbers)}\n总和: {sum(numbers)}"
        
        # 尝试解析为逗号分隔的数字
        if ',' in data:
            numbers = [float(x.strip()) for x in data.split(',')]
            avg = sum(numbers) / len(numbers)
            return f"数据分析结果:\n数量: {len(numbers)}\n平均值: {avg:.2f}\n最大值: {max(numbers)}\n最小值: {min(numbers)}\n总和: {sum(numbers)}"
        
        # 文本分析
        words = data.split()
        return f"文本分析结果:\n字符数: {len(data)}\n单词数: {len(words)}\n行数: {len(data.splitlines())}"
        
    except Exception as e:
        return f"数据分析失败: {str(e)}。支持格式: [1,2,3,4] 或 1,2,3,4 或普通文本" 