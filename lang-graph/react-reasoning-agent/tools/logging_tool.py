import json
import time
from datetime import datetime
from typing import Any, Dict, List

from langchain_core.tools import tool

from .tool_types import (
    LogExportOutput,
    LogPerformanceOutput,
    LogReasoningInput,
    LogReasoningOutput,
    LogSummaryOutput,
    LogToolUsageInput,
    LogToolUsageOutput,
)

# 全局日志存储
_reasoning_logs: List[Dict[str, Any]] = []
_tool_usage_logs: List[Dict[str, Any]] = []


@tool
def log_reasoning_step(step_type: str, content: str, iteration: int = 0) -> Dict[str, Any]:
    """记录推理步骤日志

    Args:
        step_type: 步骤类型 (thinking, action, observation, conclusion)
        content: 日志内容
        iteration: 推理轮次

    Returns:
        包含日志记录结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "step_type": str,
            "content": str,
            "iteration": int,
            "timestamp": str
        }
    """
    try:
        global _reasoning_logs

        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "iteration": iteration,
            "step_type": step_type,
            "content": content,
            "duration": None  # 可以后续计算
        }

        _reasoning_logs.append(log_entry)

        return {
            "status": "success",
            "message": f"已记录{step_type}日志",
            "step_type": step_type,
            "content": content,
            "iteration": iteration,
            "timestamp": timestamp
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"记录推理步骤失败: {str(e)}",
            "step_type": step_type,
            "content": content,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat()
        }


@tool
def log_tool_usage(
    tool_name: str,
    tool_args: Dict[str, Any],
    execution_time: float = 0.0,
    result_summary: str = ""
) -> Dict[str, Any]:
    """记录工具使用日志

    Args:
        tool_name: 工具名称
        tool_args: 工具参数
        execution_time: 执行时间（秒）
        result_summary: 结果摘要

    Returns:
        包含工具使用日志的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "tool_name": str,
            "execution_time": float,
            "success": bool,
            "timestamp": str
        }
    """
    try:
        global _tool_usage_logs

        timestamp = datetime.now().isoformat()
        success = "错误" not in result_summary and "失败" not in result_summary

        log_entry = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "arguments": tool_args,
            "execution_time": execution_time,
            "result_summary": result_summary,
            "success": success
        }

        _tool_usage_logs.append(log_entry)

        return {
            "status": "success",
            "message": f"已记录工具使用: {tool_name}",
            "tool_name": tool_name,
            "execution_time": execution_time,
            "success": success,
            "timestamp": timestamp
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"记录工具使用失败: {str(e)}",
            "tool_name": tool_name,
            "execution_time": execution_time,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }


@tool
def get_reasoning_summary() -> Dict[str, Any]:
    """获取完整的推理过程摘要

    Returns:
        包含推理摘要的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "total_reasoning_steps": int,
            "total_tool_calls": int,
            "total_execution_time": float,
            "iterations": List[Dict[str, Any]],
            "tool_statistics": Dict[str, Dict[str, Any]]
        }
    """
    try:
        global _reasoning_logs, _tool_usage_logs

        if not _reasoning_logs:
            return {
                "status": "success",
                "message": "暂无推理日志记录",
                "total_reasoning_steps": 0,
                "total_tool_calls": 0,
                "total_execution_time": 0.0,
                "iterations": [],
                "tool_statistics": {}
            }

        # 按轮次组织推理步骤
        iterations = {}
        for log in _reasoning_logs:
            iter_num = log["iteration"]
            if iter_num not in iterations:
                iterations[iter_num] = []
            iterations[iter_num].append(log)

        # 转换为列表格式
        iterations_list = []
        for iter_num in sorted(iterations.keys()):
            iterations_list.append({
                "iteration": iter_num,
                "steps": iterations[iter_num]
            })

        # 工具使用统计
        tool_statistics = {}
        total_execution_time = 0.0

        for log in _tool_usage_logs:
            tool_name = log["tool_name"]
            exec_time = log["execution_time"]

            if tool_name not in tool_statistics:
                tool_statistics[tool_name] = {
                    "count": 0,
                    "total_time": 0.0,
                    "success_count": 0,
                    "success_rate": 0.0
                }

            tool_statistics[tool_name]["count"] += 1
            tool_statistics[tool_name]["total_time"] += exec_time
            tool_statistics[tool_name]["success_count"] += 1 if log["success"] else 0
            total_execution_time += exec_time

        # 计算成功率
        for tool_name in tool_statistics:
            success_count = tool_statistics[tool_name]["success_count"]
            total_count = tool_statistics[tool_name]["count"]
            tool_statistics[tool_name]["success_rate"] = (
                success_count / total_count) * 100

        return {
            "status": "success",
            "message": "推理摘要生成完成",
            "total_reasoning_steps": len(_reasoning_logs),
            "total_tool_calls": len(_tool_usage_logs),
            "total_execution_time": total_execution_time,
            "iterations": iterations_list,
            "tool_statistics": tool_statistics
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成推理摘要失败: {str(e)}",
            "total_reasoning_steps": 0,
            "total_tool_calls": 0,
            "total_execution_time": 0.0,
            "iterations": [],
            "tool_statistics": {}
        }


@tool
def get_tool_performance_report() -> Dict[str, Any]:
    """获取工具性能报告

    Returns:
        包含工具性能分析的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "total_calls": int,
            "success_rate": float,
            "average_execution_time": float,
            "fastest_execution": float,
            "slowest_execution": float,
            "tool_rankings": List[Dict[str, Any]]
        }
    """
    try:
        global _tool_usage_logs

        if not _tool_usage_logs:
            return {
                "status": "success",
                "message": "暂无工具使用记录",
                "total_calls": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "fastest_execution": 0.0,
                "slowest_execution": 0.0,
                "tool_rankings": []
            }

        # 性能分析
        all_times = [log["execution_time"] for log in _tool_usage_logs]
        successful_calls = [log for log in _tool_usage_logs if log["success"]]

        success_rate = (len(successful_calls) / len(_tool_usage_logs)) * 100
        average_time = sum(all_times) / len(all_times)
        fastest_time = min(all_times)
        slowest_time = max(all_times)

        # 工具性能排行
        tool_performance = {}
        for log in _tool_usage_logs:
            tool_name = log["tool_name"]
            if tool_name not in tool_performance:
                tool_performance[tool_name] = []
            tool_performance[tool_name].append(log["execution_time"])

        # 按平均速度排序
        tool_rankings = []
        for tool_name, times in tool_performance.items():
            avg_time = sum(times) / len(times)
            tool_rankings.append({
                "tool_name": tool_name,
                "average_time": avg_time,
                "call_count": len(times),
                "total_time": sum(times)
            })

        tool_rankings.sort(key=lambda x: x["average_time"])

        return {
            "status": "success",
            "message": "工具性能报告生成完成",
            "total_calls": len(_tool_usage_logs),
            "success_rate": success_rate,
            "average_execution_time": average_time,
            "fastest_execution": fastest_time,
            "slowest_execution": slowest_time,
            "tool_rankings": tool_rankings
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成工具性能报告失败: {str(e)}",
            "total_calls": 0,
            "success_rate": 0.0,
            "average_execution_time": 0.0,
            "fastest_execution": 0.0,
            "slowest_execution": 0.0,
            "tool_rankings": []
        }


@tool
def export_logs_json() -> Dict[str, Any]:
    """导出日志为JSON格式

    Returns:
        包含完整日志数据的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "export_time": str,
            "reasoning_logs": List[Dict[str, Any]],
            "tool_usage_logs": List[Dict[str, Any]],
            "summary": Dict[str, Any]
        }
    """
    try:
        global _reasoning_logs, _tool_usage_logs

        export_time = datetime.now().isoformat()

        # 生成摘要信息
        summary = {
            "total_reasoning_steps": len(_reasoning_logs),
            "total_tool_calls": len(_tool_usage_logs),
            "export_timestamp": export_time
        }

        if _tool_usage_logs:
            total_time = sum(log["execution_time"] for log in _tool_usage_logs)
            successful_calls = len(
                [log for log in _tool_usage_logs if log["success"]])
            summary.update({
                "total_execution_time": total_time,
                "success_rate": (successful_calls / len(_tool_usage_logs)) * 100
            })

        return {
            "status": "success",
            "message": "日志导出完成",
            "export_time": export_time,
            "reasoning_logs": _reasoning_logs,
            "tool_usage_logs": _tool_usage_logs,
            "summary": summary
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"导出日志失败: {str(e)}",
            "export_time": datetime.now().isoformat(),
            "reasoning_logs": [],
            "tool_usage_logs": [],
            "summary": {}
        }


@tool
def clear_logs() -> Dict[str, Any]:
    """清除所有日志记录

    Returns:
        包含清除结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "cleared_reasoning_logs": int,
            "cleared_tool_logs": int
        }
    """
    try:
        global _reasoning_logs, _tool_usage_logs

        reasoning_count = len(_reasoning_logs)
        tool_count = len(_tool_usage_logs)

        _reasoning_logs.clear()
        _tool_usage_logs.clear()

        return {
            "status": "success",
            "message": f"已清除{reasoning_count}条推理日志和{tool_count}条工具日志",
            "cleared_reasoning_logs": reasoning_count,
            "cleared_tool_logs": tool_count
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"清除日志失败: {str(e)}",
            "cleared_reasoning_logs": 0,
            "cleared_tool_logs": 0
        }


@tool
def get_current_session_info() -> Dict[str, Any]:
    """获取当前会话信息

    Returns:
        包含会话信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "session_duration": str,
            "total_iterations": int,
            "total_reasoning_steps": int,
            "total_tool_calls": int,
            "unique_tools_used": int,
            "total_execution_time": float
        }
    """
    try:
        global _reasoning_logs, _tool_usage_logs

        if not _reasoning_logs and not _tool_usage_logs:
            return {
                "status": "success",
                "message": "当前会话暂无日志记录",
                "session_duration": "0分钟",
                "total_iterations": 0,
                "total_reasoning_steps": 0,
                "total_tool_calls": 0,
                "unique_tools_used": 0,
                "total_execution_time": 0.0
            }

        # 计算会话持续时间
        session_duration = "0分钟"
        if _reasoning_logs:
            start_time = datetime.fromisoformat(
                _reasoning_logs[0]["timestamp"])
            end_time = datetime.fromisoformat(_reasoning_logs[-1]["timestamp"])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            session_duration = f"{duration_minutes:.1f}分钟"

        # 统计信息
        total_iterations = len(
            set(log["iteration"] for log in _reasoning_logs)) if _reasoning_logs else 0
        unique_tools = set(log["tool_name"]
                           for log in _tool_usage_logs) if _tool_usage_logs else set()
        total_execution_time = sum(
            log["execution_time"] for log in _tool_usage_logs) if _tool_usage_logs else 0.0

        return {
            "status": "success",
            "message": "会话信息获取完成",
            "session_duration": session_duration,
            "total_iterations": total_iterations,
            "total_reasoning_steps": len(_reasoning_logs),
            "total_tool_calls": len(_tool_usage_logs),
            "unique_tools_used": len(unique_tools),
            "total_execution_time": total_execution_time
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取会话信息失败: {str(e)}",
            "session_duration": "未知",
            "total_iterations": 0,
            "total_reasoning_steps": 0,
            "total_tool_calls": 0,
            "unique_tools_used": 0,
            "total_execution_time": 0.0
        }
