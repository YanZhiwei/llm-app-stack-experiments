import calendar
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from langchain_core.tools import tool

from .tool_types import (
    BaseToolResponse,
    DateDifferenceInput,
    DateDifferenceOutput,
    GetCurrentTimeInput,
    GetCurrentTimeOutput,
)


@tool
def get_current_time(format_type: str = "complete") -> Dict[str, Any]:
    """获取当前时间信息

    Args:
        format_type: 输出格式类型 ("complete" | "date" | "time" | "timestamp")

    Returns:
        包含时间信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "date": str,
            "weekday": str,
            "time": str,
            "timestamp": float,
            "iso_format": str
        }
    """
    try:
        now = datetime.now()

        result: Dict[str, Any] = {
            "status": "success",
            "message": "获取时间成功",
            "date": now.strftime('%Y年%m月%d日'),
            "weekday": now.strftime('%A'),
            "time": now.strftime('%H:%M:%S'),
            "timestamp": now.timestamp(),
            "iso_format": now.isoformat()
        }

        # 根据format_type过滤输出
        if format_type == "date":
            result["message"] = "仅返回日期信息"
            result.pop("time", None)
            result.pop("timestamp", None)
            result.pop("iso_format", None)
        elif format_type == "time":
            result["message"] = "仅返回时间信息"
            result.pop("date", None)
            result.pop("weekday", None)
            result.pop("timestamp", None)
            result.pop("iso_format", None)
        elif format_type == "timestamp":
            result["message"] = "仅返回时间戳"
            result.pop("date", None)
            result.pop("weekday", None)
            result.pop("time", None)
            result.pop("iso_format", None)

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取时间失败: {str(e)}",
            "date": "",
            "weekday": "",
            "time": "",
            "timestamp": 0.0,
            "iso_format": ""
        }


@tool
def calculate_date_difference(date1: str, date2: Optional[str] = None) -> Dict[str, Any]:
    """计算两个日期之间的差异

    Args:
        date1: 第一个日期 (格式: YYYY-MM-DD)
        date2: 第二个日期 (格式: YYYY-MM-DD)，可选，默认为当前日期

    Returns:
        包含日期差异信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "days": int,
            "weeks": int,
            "months": int,
            "years": float,
            "is_future": bool
        }
    """
    try:
        # 解析第一个日期
        d1 = datetime.strptime(date1, "%Y-%m-%d")

        # 解析第二个日期或使用当前日期
        d2 = datetime.strptime(date2, "%Y-%m-%d") if date2 else datetime.now()

        # 计算差异
        diff = d2 - d1
        days = diff.days

        return {
            "status": "success",
            "message": "日期差异计算成功",
            "days": abs(days),
            "weeks": abs(days) // 7,
            "months": abs(days) // 30,
            "years": abs(days) / 365.0,
            "is_future": days > 0
        }

    except ValueError as e:
        return {
            "status": "error",
            "message": f"日期格式错误: {str(e)}，请使用YYYY-MM-DD格式",
            "days": 0,
            "weeks": 0,
            "months": 0,
            "years": 0.0,
            "is_future": False
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"计算日期差异失败: {str(e)}",
            "days": 0,
            "weeks": 0,
            "months": 0,
            "years": 0.0,
            "is_future": False
        }


@tool
def get_calendar_info(year: int = 0, month: int = 0) -> str:
    """获取日历信息

    Args:
        year: 年份，为0时使用当前年份
        month: 月份，为0时使用当前月份

    Returns:
        日历信息
    """
    now = datetime.now()
    if year == 0:
        year = now.year
    if month == 0:
        month = now.month

    try:
        # 获取月历
        cal = calendar.month(year, month)

        # 获取月份信息
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]
        first_weekday = calendar.monthrange(year, month)[0]
        weekday_name = calendar.day_name[first_weekday]

        result = f"{year}年{month}月日历:\n"
        result += f"月份: {month_name}\n"
        result += f"总天数: {days_in_month}天\n"
        result += f"1号是: {weekday_name}\n"
        result += f"是否闰年: {'是' if calendar.isleap(year) else '否'}\n\n"
        result += cal

        return result

    except Exception as e:
        return f"获取日历信息失败: {e}"


@tool
def add_days_to_date(start_date: str, days: int) -> str:
    """给指定日期添加或减去天数

    Args:
        start_date: 起始日期 (格式: YYYY-MM-DD)
        days: 要添加的天数 (可以为负数)

    Returns:
        计算后的日期
    """
    try:
        # 解析起始日期
        start = datetime.strptime(start_date, "%Y-%m-%d")

        # 添加天数
        result_date = start + timedelta(days=days)

        result = f"日期计算:\n"
        result += f"起始日期: {start.strftime('%Y年%m月%d日')} ({start.strftime('%A')})\n"
        result += f"调整天数: {days}天\n"
        result += f"结果日期: {result_date.strftime('%Y年%m月%d日')} ({result_date.strftime('%A')})\n"
        result += f"标准格式: {result_date.strftime('%Y-%m-%d')}"

        return result

    except ValueError as e:
        return f"日期格式错误: {e}\n请使用 YYYY-MM-DD 格式，例如: 2024-01-15"
