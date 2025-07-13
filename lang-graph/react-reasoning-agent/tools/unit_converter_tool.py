from typing import Any, Dict

from langchain_core.tools import tool

from .tool_types import UnitConvertInput, UnitConvertOutput


@tool
def convert_length(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """长度单位转换

    Args:
        value: 数值
        from_unit: 原单位 (mm, cm, m, km, inch, ft, yard, mile)
        to_unit: 目标单位 (mm, cm, m, km, inch, ft, yard, mile)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 转换为米的系数
        to_meter = {
            'mm': 0.001,
            'cm': 0.01,
            'm': 1,
            'km': 1000,
            'inch': 0.0254,
            'ft': 0.3048,
            'yard': 0.9144,
            'mile': 1609.34
        }

        if from_unit not in to_meter or to_unit not in to_meter:
            available_units = list(to_meter.keys())
            return {
                "status": "error",
                "message": f"不支持的单位，可用单位: {', '.join(available_units)}",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 转换为米，然后转换为目标单位
        meters = value * to_meter[from_unit]
        result = meters / to_meter[to_unit]
        conversion_factor = to_meter[from_unit] / to_meter[to_unit]

        return {
            "status": "success",
            "message": f"长度转换: {value} {from_unit} = {result:.6f} {to_unit}",
            "original_value": value,
            "converted_value": round(result, 6),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }


@tool
def convert_weight(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """重量单位转换

    Args:
        value: 数值
        from_unit: 原单位 (mg, g, kg, t, oz, lb, ton)
        to_unit: 目标单位 (mg, g, kg, t, oz, lb, ton)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 转换为克的系数
        to_gram = {
            'mg': 0.001,
            'g': 1,
            'kg': 1000,
            't': 1000000,
            'oz': 28.3495,
            'lb': 453.592,
            'ton': 907185
        }

        if from_unit not in to_gram or to_unit not in to_gram:
            available_units = list(to_gram.keys())
            return {
                "status": "error",
                "message": f"不支持的单位，可用单位: {', '.join(available_units)}",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 转换为克，然后转换为目标单位
        grams = value * to_gram[from_unit]
        result = grams / to_gram[to_unit]
        conversion_factor = to_gram[from_unit] / to_gram[to_unit]

        return {
            "status": "success",
            "message": f"重量转换: {value} {from_unit} = {result:.6f} {to_unit}",
            "original_value": value,
            "converted_value": round(result, 6),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }


@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """温度单位转换

    Args:
        value: 数值
        from_unit: 原单位 (C, F, K)
        to_unit: 目标单位 (C, F, K)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 统一转换为摄氏度
        if from_unit == 'C':
            celsius = value
        elif from_unit == 'F':
            celsius = (value - 32) * 5/9
        elif from_unit == 'K':
            celsius = value - 273.15
        else:
            return {
                "status": "error",
                "message": f"不支持的温度单位 '{from_unit}'，可用单位: C(摄氏度), F(华氏度), K(开尔文)",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 从摄氏度转换为目标单位
        if to_unit == 'C':
            result = celsius
        elif to_unit == 'F':
            result = celsius * 9/5 + 32
        elif to_unit == 'K':
            result = celsius + 273.15
        else:
            return {
                "status": "error",
                "message": f"不支持的温度单位 '{to_unit}'，可用单位: C(摄氏度), F(华氏度), K(开尔文)",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 温度转换没有固定的转换因子，因为有偏移量
        conversion_factor = 1.0  # 占位符

        return {
            "status": "success",
            "message": f"温度转换: {value}°{from_unit} = {result:.2f}°{to_unit}",
            "original_value": value,
            "converted_value": round(result, 2),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }


@tool
def convert_area(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """面积单位转换

    Args:
        value: 数值
        from_unit: 原单位 (mm2, cm2, m2, km2, acre, hectare)
        to_unit: 目标单位 (mm2, cm2, m2, km2, acre, hectare)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 转换为平方米的系数
        to_m2 = {
            'mm2': 0.000001,
            'cm2': 0.0001,
            'm2': 1,
            'km2': 1000000,
            'acre': 4046.86,
            'hectare': 10000
        }

        if from_unit not in to_m2 or to_unit not in to_m2:
            available_units = list(to_m2.keys())
            return {
                "status": "error",
                "message": f"不支持的单位，可用单位: {', '.join(available_units)}",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 转换为平方米，然后转换为目标单位
        square_meters = value * to_m2[from_unit]
        result = square_meters / to_m2[to_unit]
        conversion_factor = to_m2[from_unit] / to_m2[to_unit]

        return {
            "status": "success",
            "message": f"面积转换: {value} {from_unit} = {result:.6f} {to_unit}",
            "original_value": value,
            "converted_value": round(result, 6),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }


@tool
def convert_volume(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """体积单位转换

    Args:
        value: 数值
        from_unit: 原单位 (ml, l, m3, gallon, quart, pint, cup)
        to_unit: 目标单位 (ml, l, m3, gallon, quart, pint, cup)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 转换为升的系数
        to_liter = {
            'ml': 0.001,
            'l': 1,
            'm3': 1000,
            'gallon': 3.78541,
            'quart': 0.946353,
            'pint': 0.473176,
            'cup': 0.236588
        }

        if from_unit not in to_liter or to_unit not in to_liter:
            available_units = list(to_liter.keys())
            return {
                "status": "error",
                "message": f"不支持的单位，可用单位: {', '.join(available_units)}",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 转换为升，然后转换为目标单位
        liters = value * to_liter[from_unit]
        result = liters / to_liter[to_unit]
        conversion_factor = to_liter[from_unit] / to_liter[to_unit]

        return {
            "status": "success",
            "message": f"体积转换: {value} {from_unit} = {result:.6f} {to_unit}",
            "original_value": value,
            "converted_value": round(result, 6),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }


@tool
def convert_speed(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """速度单位转换

    Args:
        value: 数值
        from_unit: 原单位 (mps, kmh, mph, knot)
        to_unit: 目标单位 (mps, kmh, mph, knot)

    Returns:
        包含转换结果的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "original_value": float,
            "converted_value": float,
            "from_unit": str,
            "to_unit": str,
            "conversion_factor": float
        }
    """
    try:
        # 转换为米每秒的系数
        to_mps = {
            'mps': 1,          # 米每秒
            'kmh': 1/3.6,      # 公里每小时
            'mph': 0.44704,    # 英里每小时
            'knot': 0.514444   # 节
        }

        if from_unit not in to_mps or to_unit not in to_mps:
            available_units = list(to_mps.keys())
            return {
                "status": "error",
                "message": f"不支持的单位，可用单位: {', '.join(available_units)}",
                "original_value": value,
                "converted_value": 0.0,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "conversion_factor": 0.0
            }

        # 转换为米每秒，然后转换为目标单位
        mps = value * to_mps[from_unit]
        result = mps / to_mps[to_unit]
        conversion_factor = to_mps[from_unit] / to_mps[to_unit]

        return {
            "status": "success",
            "message": f"速度转换: {value} {from_unit} = {result:.6f} {to_unit}",
            "original_value": value,
            "converted_value": round(result, 6),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": conversion_factor
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"转换失败: {str(e)}",
            "original_value": value,
            "converted_value": 0.0,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "conversion_factor": 0.0
        }
