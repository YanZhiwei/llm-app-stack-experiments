import json
import re
from collections import Counter
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from .tool_types import (
    PatternExtractInput,
    PatternExtractOutput,
    TextAnalysisInput,
    TextAnalysisOutput,
    TextFormatInput,
    TextFormatOutput,
    TextSimilarityInput,
    TextSimilarityOutput,
)


@tool
def analyze_text(text: str) -> Dict[str, Any]:
    """分析文本的详细信息

    Args:
        text: 要分析的文本内容

    Returns:
        包含文本分析结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "char_count": int,
            "word_count": int,
            "line_count": int,
            "paragraph_count": int,
            "sentence_count": int,
            "language_features": Dict[str, bool],
            "most_common_words": List[Dict[str, Any]],
            "readability_metrics": Dict[str, float]
        }
    """
    try:
        if not text.strip():
            return {
                "status": "error",
                "message": "文本内容为空",
                "char_count": 0,
                "word_count": 0,
                "line_count": 0,
                "paragraph_count": 0,
                "sentence_count": 0,
                "language_features": {},
                "most_common_words": [],
                "readability_metrics": {}
            }

        # 基本统计
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])

        # 句子计数
        sentence_count = len(re.findall(r'[.!?]+', text))

        # 字符频率分析
        char_freq = Counter(text.lower())
        most_common_chars = char_freq.most_common(5)

        # 词频分析
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        most_common_words = [{"word": word, "count": count}
                             for word, count in word_freq.most_common(5)]

        # 语言特征检测
        language_features = {
            "has_chinese": bool(re.search(r'[\u4e00-\u9fff]', text)),
            "has_english": bool(re.search(r'[a-zA-Z]', text)),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_punctuation": bool(re.search(r'[^\w\s]', text))
        }

        # 可读性指标
        readability_metrics = {
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "avg_sentence_length": word_count / max(sentence_count, 1),
            "avg_line_length": char_count / line_count if line_count > 0 else 0
        }

        return {
            "status": "success",
            "message": "文本分析完成",
            "char_count": char_count,
            "word_count": word_count,
            "line_count": line_count,
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "language_features": language_features,
            "most_common_words": most_common_words,
            "readability_metrics": readability_metrics
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"文本分析失败: {str(e)}",
            "char_count": 0,
            "word_count": 0,
            "line_count": 0,
            "paragraph_count": 0,
            "sentence_count": 0,
            "language_features": {},
            "most_common_words": [],
            "readability_metrics": {}
        }


@tool
def format_text(text: str, operation: str) -> Dict[str, Any]:
    """格式化文本

    Args:
        text: 要格式化的文本
        operation: 格式化操作

    Returns:
        包含格式化结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_text": str,
            "formatted_text": str,
            "operation": str
        }
    """
    try:
        if not text:
            return {
                "status": "error",
                "message": "文本内容为空",
                "original_text": "",
                "formatted_text": "",
                "operation": operation
            }

        operations = {
            "upper": lambda t: t.upper(),
            "lower": lambda t: t.lower(),
            "title": lambda t: t.title(),
            "capitalize": lambda t: t.capitalize(),
            "reverse": lambda t: t[::-1],
            "remove_spaces": lambda t: t.replace(' ', ''),
            "remove_extra_spaces": lambda t: ' '.join(t.split()),
            "snake_case": lambda t: '_'.join(t.lower().split()),
            "camel_case": lambda t: ''.join(word.capitalize() for word in t.split()),
            "kebab_case": lambda t: '-'.join(t.lower().split())
        }

        if operation not in operations:
            available_ops = list(operations.keys())
            return {
                "status": "error",
                "message": f"不支持的操作 '{operation}'，可用操作: {', '.join(available_ops)}",
                "original_text": text,
                "formatted_text": "",
                "operation": operation
            }

        formatted_text = operations[operation](text)

        return {
            "status": "success",
            "message": "文本格式化成功",
            "original_text": text,
            "formatted_text": formatted_text,
            "operation": operation
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"格式化失败: {str(e)}",
            "original_text": text,
            "formatted_text": "",
            "operation": operation
        }


@tool
def extract_patterns(text: str, pattern_type: str) -> Dict[str, Any]:
    """从文本中提取特定模式

    Args:
        text: 源文本
        pattern_type: 模式类型

    Returns:
        包含提取结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "pattern_type": str,
            "matches": List[str],
            "unique_matches": List[str],
            "match_count": int
        }
    """
    try:
        if not text:
            return {
                "status": "error",
                "message": "文本内容为空",
                "pattern_type": pattern_type,
                "matches": [],
                "unique_matches": [],
                "match_count": 0
            }

        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            "phone": r'(?:\+?86)?[-\s]?(?:\d{3}[-\s]?\d{4}[-\s]?\d{4}|\d{3}[-\s]?\d{8})',
            "number": r'-?\d+(?:\.\d+)?',
            "chinese": r'[\u4e00-\u9fff]+',
            "english": r'[a-zA-Z]+',
            "ip": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "date": r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            "time": r'\d{1,2}:\d{2}(?::\d{2})?'
        }

        if pattern_type not in patterns:
            available_patterns = list(patterns.keys())
            return {
                "status": "error",
                "message": f"不支持的模式类型 '{pattern_type}'，可用模式: {', '.join(available_patterns)}",
                "pattern_type": pattern_type,
                "matches": [],
                "unique_matches": [],
                "match_count": 0
            }

        matches = re.findall(patterns[pattern_type], text)
        unique_matches = list(set(matches))

        return {
            "status": "success",
            "message": f"模式提取完成，找到{len(matches)}个匹配项",
            "pattern_type": pattern_type,
            "matches": matches,
            "unique_matches": unique_matches,
            "match_count": len(matches)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"模式提取失败: {str(e)}",
            "pattern_type": pattern_type,
            "matches": [],
            "unique_matches": [],
            "match_count": 0
        }


@tool
def text_similarity(text1: str, text2: str) -> Dict[str, Any]:
    """计算两个文本的相似度

    Args:
        text1: 第一个文本
        text2: 第二个文本

    Returns:
        包含相似度分析结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "char_similarity": float,
            "word_similarity": float,
            "length_ratio": float,
            "overall_similarity": float
        }
    """
    try:
        if not text1 or not text2:
            return {
                "status": "error",
                "message": "两个文本都不能为空",
                "char_similarity": 0.0,
                "word_similarity": 0.0,
                "length_ratio": 0.0,
                "overall_similarity": 0.0
            }

        # 简单的相似度计算
        def jaccard_similarity(set1, set2):
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0

        # 字符级别相似度
        chars1 = set(text1.lower())
        chars2 = set(text2.lower())
        char_similarity = jaccard_similarity(chars1, chars2)

        # 词级别相似度
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        word_similarity = jaccard_similarity(words1, words2)

        # 长度差异
        length_ratio = min(len(text1), len(text2)) / \
            max(len(text1), len(text2))

        # 综合相似度
        overall_similarity = (
            char_similarity + word_similarity + length_ratio) / 3

        return {
            "status": "success",
            "message": "文本相似度计算完成",
            "char_similarity": round(char_similarity, 4),
            "word_similarity": round(word_similarity, 4),
            "length_ratio": round(length_ratio, 4),
            "overall_similarity": round(overall_similarity, 4)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"相似度计算失败: {str(e)}",
            "char_similarity": 0.0,
            "word_similarity": 0.0,
            "length_ratio": 0.0,
            "overall_similarity": 0.0
        }
