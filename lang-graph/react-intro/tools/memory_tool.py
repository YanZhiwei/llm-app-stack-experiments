from langchain_core.tools import tool
from typing import Dict, List

# 简单的内存存储
_memory_store: Dict[str, str] = {}
_memory_history: List[str] = []

@tool
def store_memory(key: str, value: str) -> str:
    """存储信息到记忆中
    
    Args:
        key: 信息的关键词或标题
        value: 要存储的信息内容
    
    Returns:
        存储确认信息
    """
    global _memory_store, _memory_history
    
    _memory_store[key] = value
    _memory_history.append(f"存储: {key}")
    
    return f"成功存储信息到记忆中:\n关键词: {key}\n内容: {value}\n\n当前记忆库包含 {len(_memory_store)} 条信息"

@tool  
def retrieve_memory(key: str = "") -> str:
    """从记忆中检索信息
    
    Args:
        key: 要检索的关键词，为空时返回所有记忆
    
    Returns:
        检索到的信息
    """
    global _memory_store, _memory_history
    
    if not key:
        # 返回所有记忆
        if not _memory_store:
            return "记忆库为空，没有存储任何信息"
        
        result = "记忆库中的所有信息:\n\n"
        for i, (k, v) in enumerate(_memory_store.items(), 1):
            result += f"{i}. {k}: {v}\n\n"
        
        result += f"记忆历史: {' -> '.join(_memory_history[-5:])}"  # 显示最近5条历史
        return result
    
    # 精确匹配
    if key in _memory_store:
        return f"找到记忆:\n关键词: {key}\n内容: {_memory_store[key]}"
    
    # 模糊匹配
    key_lower = key.lower()
    matches = []
    for k, v in _memory_store.items():
        if key_lower in k.lower() or any(word in k.lower() for word in key_lower.split()):
            matches.append((k, v))
    
    if matches:
        result = f"模糊匹配到 {len(matches)} 条相关记忆:\n\n"
        for k, v in matches:
            result += f"- {k}: {v}\n\n"
        return result
    
    return f"未找到关键词 '{key}' 相关的记忆\n\n可用的记忆关键词: {list(_memory_store.keys())}" 