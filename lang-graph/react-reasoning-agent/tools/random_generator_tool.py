import random
import secrets
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

from langchain_core.tools import tool

from .tool_types import (
    RandomNumbersInput,
    RandomNumbersOutput,
    RandomPasswordInput,
    RandomPasswordOutput,
)


@tool
def generate_password(
    length: int = 12,
    include_symbols: bool = True,
    include_numbers: bool = True,
    include_uppercase: bool = True,
    include_lowercase: bool = True
) -> Dict[str, Any]:
    """生成随机密码

    Args:
        length: 密码长度
        include_symbols: 是否包含特殊字符
        include_numbers: 是否包含数字
        include_uppercase: 是否包含大写字母
        include_lowercase: 是否包含小写字母

    Returns:
        包含密码生成结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "password": str,
            "length": int,
            "strength_level": str,
            "strength_score": int,
            "character_types": List[str],
            "character_set_size": int
        }
    """
    try:
        if length < 4:
            return {
                "status": "error",
                "message": "密码长度不能小于4位",
                "password": "",
                "length": length,
                "strength_level": "无效",
                "strength_score": 0,
                "character_types": [],
                "character_set_size": 0
            }

        if length > 128:
            return {
                "status": "error",
                "message": "密码长度不能超过128位",
                "password": "",
                "length": length,
                "strength_level": "无效",
                "strength_score": 0,
                "character_types": [],
                "character_set_size": 0
            }

        # 构建字符集
        chars = ""
        character_types = []

        if include_lowercase:
            chars += string.ascii_lowercase
            character_types.append("小写字母")
        if include_uppercase:
            chars += string.ascii_uppercase
            character_types.append("大写字母")
        if include_numbers:
            chars += string.digits
            character_types.append("数字")
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            character_types.append("特殊字符")

        if not chars:
            return {
                "status": "error",
                "message": "至少需要选择一种字符类型",
                "password": "",
                "length": length,
                "strength_level": "无效",
                "strength_score": 0,
                "character_types": [],
                "character_set_size": 0
            }

        # 生成密码
        password = ''.join(secrets.choice(chars) for _ in range(length))

        # 分析密码强度
        strength_score = len(character_types)
        if length >= 12:
            strength_score += 1

        if strength_score >= 5:
            strength_level = "很强"
        elif strength_score >= 4:
            strength_level = "强"
        elif strength_score >= 3:
            strength_level = "中等"
        elif strength_score >= 2:
            strength_level = "弱"
        else:
            strength_level = "很弱"

        return {
            "status": "success",
            "message": f"成功生成{length}位密码，强度：{strength_level}",
            "password": password,
            "length": length,
            "strength_level": strength_level,
            "strength_score": strength_score,
            "character_types": character_types,
            "character_set_size": len(chars)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成密码失败: {str(e)}",
            "password": "",
            "length": length,
            "strength_level": "错误",
            "strength_score": 0,
            "character_types": [],
            "character_set_size": 0
        }


@tool
def generate_random_numbers(
    count: int = 5,
    min_value: int = 1,
    max_value: int = 100,
    allow_duplicates: bool = True
) -> Dict[str, Any]:
    """生成随机数

    Args:
        count: 生成数量
        min_value: 最小值
        max_value: 最大值
        allow_duplicates: 是否允许重复

    Returns:
        包含随机数生成结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "numbers": List[int],
            "count": int,
            "min_value": int,
            "max_value": int,
            "allow_duplicates": bool,
            "statistics": Dict[str, Any]
        }
    """
    try:
        if count <= 0:
            return {
                "status": "error",
                "message": "生成数量必须大于0",
                "numbers": [],
                "count": count,
                "min_value": min_value,
                "max_value": max_value,
                "allow_duplicates": allow_duplicates,
                "statistics": {}
            }

        if count > 1000:
            return {
                "status": "error",
                "message": "生成数量不能超过1000",
                "numbers": [],
                "count": count,
                "min_value": min_value,
                "max_value": max_value,
                "allow_duplicates": allow_duplicates,
                "statistics": {}
            }

        if min_value > max_value:
            return {
                "status": "error",
                "message": "最小值不能大于最大值",
                "numbers": [],
                "count": count,
                "min_value": min_value,
                "max_value": max_value,
                "allow_duplicates": allow_duplicates,
                "statistics": {}
            }

        if not allow_duplicates and count > (max_value - min_value + 1):
            return {
                "status": "error",
                "message": f"在不允许重复的情况下，生成数量不能超过范围大小 ({max_value - min_value + 1})",
                "numbers": [],
                "count": count,
                "min_value": min_value,
                "max_value": max_value,
                "allow_duplicates": allow_duplicates,
                "statistics": {}
            }

        if allow_duplicates:
            numbers = [random.randint(min_value, max_value)
                       for _ in range(count)]
        else:
            numbers = random.sample(range(min_value, max_value + 1), count)

        # 计算统计信息
        statistics = {
            "max": max(numbers),
            "min": min(numbers),
            "average": sum(numbers) / len(numbers),
            "sum": sum(numbers),
            "unique_count": len(set(numbers))
        }

        return {
            "status": "success",
            "message": f"成功生成{count}个随机数",
            "numbers": numbers,
            "count": count,
            "min_value": min_value,
            "max_value": max_value,
            "allow_duplicates": allow_duplicates,
            "statistics": statistics
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成随机数失败: {str(e)}",
            "numbers": [],
            "count": count,
            "min_value": min_value,
            "max_value": max_value,
            "allow_duplicates": allow_duplicates,
            "statistics": {}
        }


@tool
def generate_uuid(version: int = 4, count: int = 1) -> Dict[str, Any]:
    """生成UUID

    Args:
        version: UUID版本 (1, 4)
        count: 生成数量

    Returns:
        包含UUID生成结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "uuids": List[str],
            "version": int,
            "count": int,
            "format_type": str
        }
    """
    try:
        if count <= 0:
            return {
                "status": "error",
                "message": "生成数量必须大于0",
                "uuids": [],
                "version": version,
                "count": count,
                "format_type": "standard"
            }

        if count > 100:
            return {
                "status": "error",
                "message": "生成数量不能超过100",
                "uuids": [],
                "version": version,
                "count": count,
                "format_type": "standard"
            }

        if version not in [1, 4]:
            return {
                "status": "error",
                "message": "仅支持UUID版本1和4",
                "uuids": [],
                "version": version,
                "count": count,
                "format_type": "standard"
            }

        uuids = []
        for _ in range(count):
            if version == 1:
                uuids.append(str(uuid.uuid1()))
            else:  # version == 4
                uuids.append(str(uuid.uuid4()))

        format_description = "基于时间戳和MAC地址" if version == 1 else "基于随机数"

        return {
            "status": "success",
            "message": f"成功生成{count}个UUID v{version}",
            "uuids": uuids,
            "version": version,
            "count": count,
            "format_type": format_description
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成UUID失败: {str(e)}",
            "uuids": [],
            "version": version,
            "count": count,
            "format_type": "error"
        }


@tool
def generate_random_text(length: int = 100, text_type: str = "mixed") -> Dict[str, Any]:
    """生成随机文本

    Args:
        length: 文本长度
        text_type: 文本类型 - "letters"(字母), "numbers"(数字), "mixed"(混合), "chinese"(中文)

    Returns:
        包含随机文本生成结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "text": str,
            "length": int,
            "text_type": str,
            "character_count": int
        }
    """
    try:
        if length <= 0:
            return {
                "status": "error",
                "message": "文本长度必须大于0",
                "text": "",
                "length": length,
                "text_type": text_type,
                "character_count": 0
            }

        if length > 10000:
            return {
                "status": "error",
                "message": "文本长度不能超过10000",
                "text": "",
                "length": length,
                "text_type": text_type,
                "character_count": 0
            }

        if text_type == "letters":
            chars = string.ascii_letters
        elif text_type == "numbers":
            chars = string.digits
        elif text_type == "mixed":
            chars = string.ascii_letters + string.digits + " "
        elif text_type == "chinese":
            # 简化处理，使用常用汉字
            chars = "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严"
        else:
            return {
                "status": "error",
                "message": "不支持的文本类型，可用类型: letters, numbers, mixed, chinese",
                "text": "",
                "length": length,
                "text_type": text_type,
                "character_count": 0
            }

        text = ''.join(random.choice(chars) for _ in range(length))

        return {
            "status": "success",
            "message": f"成功生成{length}个字符的{text_type}类型文本",
            "text": text,
            "length": length,
            "text_type": text_type,
            "character_count": len(text)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成随机文本失败: {str(e)}",
            "text": "",
            "length": length,
            "text_type": text_type,
            "character_count": 0
        }


@tool
def generate_random_choice(options: str, count: int = 1) -> Dict[str, Any]:
    """从选项中随机选择

    Args:
        options: 选项列表，用逗号分隔
        count: 选择数量

    Returns:
        包含随机选择结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "choices": List[str],
            "options": List[str],
            "count": int
        }
    """
    try:
        if not options.strip():
            return {
                "status": "error",
                "message": "选项不能为空",
                "choices": [],
                "options": [],
                "count": count
            }

        # 解析选项
        option_list = [opt.strip()
                       for opt in options.split(',') if opt.strip()]

        if not option_list:
            return {
                "status": "error",
                "message": "未找到有效选项",
                "choices": [],
                "options": [],
                "count": count
            }

        if count <= 0:
            return {
                "status": "error",
                "message": "选择数量必须大于0",
                "choices": [],
                "options": option_list,
                "count": count
            }

        if count > len(option_list):
            return {
                "status": "error",
                "message": f"选择数量不能超过选项数量 ({len(option_list)})",
                "choices": [],
                "options": option_list,
                "count": count
            }

        # 随机选择
        choices = random.sample(option_list, count)

        return {
            "status": "success",
            "message": f"从{len(option_list)}个选项中随机选择了{count}个",
            "choices": choices,
            "options": option_list,
            "count": count
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"随机选择失败: {str(e)}",
            "choices": [],
            "options": [],
            "count": count
        }


@tool
def generate_random_date(start_date: str = "2020-01-01", end_date: str = "2024-12-31", count: int = 1) -> Dict[str, Any]:
    """生成随机日期

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        count: 生成数量

    Returns:
        包含随机日期生成结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "dates": List[str],
            "start_date": str,
            "end_date": str,
            "count": int
        }
    """
    try:
        if count <= 0:
            return {
                "status": "error",
                "message": "生成数量必须大于0",
                "dates": [],
                "start_date": start_date,
                "end_date": end_date,
                "count": count
            }

        if count > 100:
            return {
                "status": "error",
                "message": "生成数量不能超过100",
                "dates": [],
                "start_date": start_date,
                "end_date": end_date,
                "count": count
            }

        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if start_dt > end_dt:
            return {
                "status": "error",
                "message": "开始日期不能晚于结束日期",
                "dates": [],
                "start_date": start_date,
                "end_date": end_date,
                "count": count
            }

        # 计算日期范围
        date_range = (end_dt - start_dt).days + 1

        if date_range <= 0:
            return {
                "status": "error",
                "message": "日期范围无效",
                "dates": [],
                "start_date": start_date,
                "end_date": end_date,
                "count": count
            }

        # 生成随机日期
        dates = []
        for _ in range(count):
            random_days = random.randint(0, date_range - 1)
            random_date = start_dt + timedelta(days=random_days)
            dates.append(random_date.strftime("%Y-%m-%d"))

        return {
            "status": "success",
            "message": f"成功生成{count}个随机日期",
            "dates": dates,
            "start_date": start_date,
            "end_date": end_date,
            "count": count
        }

    except ValueError as e:
        return {
            "status": "error",
            "message": f"日期格式错误: {str(e)}",
            "dates": [],
            "start_date": start_date,
            "end_date": end_date,
            "count": count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"生成随机日期失败: {str(e)}",
            "dates": [],
            "start_date": start_date,
            "end_date": end_date,
            "count": count
        }
