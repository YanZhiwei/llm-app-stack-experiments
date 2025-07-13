from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from .tool_types import (
    MemoryRetrieveInput,
    MemoryRetrieveOutput,
    MemoryStoreInput,
    MemoryStoreOutput,
)

# 简单的内存存储
_memory_store: Dict[str, str] = {}
_memory_history: List[str] = []


@tool
def store_memory(key: str, value: str) -> Dict[str, Any]:
    """存储信息到记忆中

    Args:
        key: 信息的关键词或标题
        value: 要存储的信息内容

    Returns:
        包含存储结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "key": str,
            "value": str,
            "total_memories": int
        }
    """
    try:
        global _memory_store, _memory_history

        if not key.strip():
            return {
                "status": "error",
                "message": "关键词不能为空",
                "key": "",
                "value": "",
                "total_memories": len(_memory_store)
            }

        if not value.strip():
            return {
                "status": "error",
                "message": "存储内容不能为空",
                "key": key,
                "value": "",
                "total_memories": len(_memory_store)
            }

        _memory_store[key] = value
        _memory_history.append(f"存储: {key}")

        return {
            "status": "success",
            "message": f"成功存储信息到记忆中",
            "key": key,
            "value": value,
            "total_memories": len(_memory_store)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"存储失败: {str(e)}",
            "key": key,
            "value": value,
            "total_memories": len(_memory_store)
        }


@tool
def retrieve_memory(key: Optional[str] = None) -> Dict[str, Any]:
    """从记忆中检索信息

    Args:
        key: 要检索的关键词，为空时返回所有记忆

    Returns:
        包含检索结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "key": Optional[str],
            "memories": List[Dict[str, str]],
            "total_count": int
        }
    """
    try:
        global _memory_store, _memory_history

        if not key:
            # 返回所有记忆
            if not _memory_store:
                return {
                    "status": "success",
                    "message": "记忆库为空，没有存储任何信息",
                    "key": None,
                    "memories": [],
                    "total_count": 0
                }

            memories = [{"key": k, "value": v}
                        for k, v in _memory_store.items()]

            return {
                "status": "success",
                "message": f"检索到所有记忆，共{len(memories)}条",
                "key": None,
                "memories": memories,
                "total_count": len(memories)
            }

        # 精确匹配
        if key in _memory_store:
            return {
                "status": "success",
                "message": "找到精确匹配的记忆",
                "key": key,
                "memories": [{"key": key, "value": _memory_store[key]}],
                "total_count": 1
            }

        # 模糊匹配
        key_lower = key.lower()
        matches = []
        for k, v in _memory_store.items():
            if key_lower in k.lower() or any(word in k.lower() for word in key_lower.split()):
                matches.append({"key": k, "value": v})

        if matches:
            return {
                "status": "success",
                "message": f"模糊匹配到{len(matches)}条相关记忆",
                "key": key,
                "memories": matches,
                "total_count": len(matches)
            }

        return {
            "status": "success",
            "message": f"未找到关键词 '{key}' 相关的记忆",
            "key": key,
            "memories": [],
            "total_count": 0
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"检索失败: {str(e)}",
            "key": key,
            "memories": [],
            "total_count": 0
        }
