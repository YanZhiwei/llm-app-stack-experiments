import json
import urllib.parse
from typing import Any, Dict, List, Optional

import requests
from langchain_core.tools import tool

from .tool_types import (
    ExchangeRateInput,
    ExchangeRateOutput,
    WeatherInput,
    WeatherOutput,
)


@tool
def get_weather_info(city: str, country: Optional[str] = "CN") -> Dict[str, Any]:
    """获取天气信息 (使用免费API)

    Args:
        city: 城市名称
        country: 国家代码，可选，默认CN

    Returns:
        包含天气信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "temperature": float,
            "feels_like": float,
            "humidity": int,
            "description": str,
            "wind_speed": float,
            "visibility": float,
            "pressure": float,
            "observation_time": str
        }
    """
    try:
        country = country or "CN"

        # 使用 wttr.in 的免费天气API
        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'current_condition' in data:
            current = data['current_condition'][0]
            weather_desc = current.get('lang_zh', [{}])[0].get(
                'value', current.get('weatherDesc', [{}])[0].get('value', ''))

            return {
                "status": "success",
                "message": f"成功获取{city}天气信息",
                "temperature": float(current.get('temp_C', 0)),
                "feels_like": float(current.get('FeelsLikeC', 0)),
                "humidity": int(current.get('humidity', 0)),
                "description": weather_desc,
                "wind_speed": float(current.get('windspeedKmph', 0)),
                "visibility": float(current.get('visibility', 0)),
                "pressure": float(current.get('pressure', 0)),
                "observation_time": current.get('observation_time', '')
            }
        else:
            return {
                "status": "error",
                "message": f"无法获取 {city} 的天气信息，请检查城市名称是否正确",
                "temperature": 0.0,
                "feels_like": 0.0,
                "humidity": 0,
                "description": "",
                "wind_speed": 0.0,
                "visibility": 0.0,
                "pressure": 0.0,
                "observation_time": ""
            }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"网络请求失败: {str(e)}",
            "temperature": 0.0,
            "feels_like": 0.0,
            "humidity": 0,
            "description": "",
            "wind_speed": 0.0,
            "visibility": 0.0,
            "pressure": 0.0,
            "observation_time": ""
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "天气数据解析失败",
            "temperature": 0.0,
            "feels_like": 0.0,
            "humidity": 0,
            "description": "",
            "wind_speed": 0.0,
            "visibility": 0.0,
            "pressure": 0.0,
            "observation_time": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取天气信息失败: {str(e)}",
            "temperature": 0.0,
            "feels_like": 0.0,
            "humidity": 0,
            "description": "",
            "wind_speed": 0.0,
            "visibility": 0.0,
            "pressure": 0.0,
            "observation_time": ""
        }


@tool
def get_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """获取汇率信息 (使用免费API)

    Args:
        from_currency: 源货币代码 (如 USD, EUR, JPY)
        to_currency: 目标货币代码 (如 CNY, USD, EUR)

    Returns:
        包含汇率信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "rate": float,
            "base_currency": str,
            "target_currency": str,
            "update_time": str,
            "examples": List[dict]
        }
    """
    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # 使用 exchangerate-api.com 的免费API
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'rates' in data and to_currency in data['rates']:
            rate = data['rates'][to_currency]
            base_currency = data['base']

            # 生成换算示例
            examples = [
                {"amount": 1, "result": rate},
                {"amount": 100, "result": rate * 100},
                {"amount": 1000, "result": rate * 1000}
            ]

            return {
                "status": "success",
                "message": f"成功获取{from_currency}到{to_currency}的汇率",
                "rate": rate,
                "base_currency": base_currency,
                "target_currency": to_currency,
                "update_time": data.get('date', ''),
                "examples": examples
            }
        else:
            return {
                "status": "error",
                "message": f"不支持的货币代码: {to_currency}",
                "rate": 0.0,
                "base_currency": from_currency,
                "target_currency": to_currency,
                "update_time": "",
                "examples": []
            }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"网络请求失败: {str(e)}",
            "rate": 0.0,
            "base_currency": from_currency,
            "target_currency": to_currency,
            "update_time": "",
            "examples": []
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "汇率数据解析失败",
            "rate": 0.0,
            "base_currency": from_currency,
            "target_currency": to_currency,
            "update_time": "",
            "examples": []
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取汇率信息失败: {str(e)}",
            "rate": 0.0,
            "base_currency": from_currency,
            "target_currency": to_currency,
            "update_time": "",
            "examples": []
        }


@tool
def get_ip_location(ip: str = "") -> str:
    """获取IP地址的地理位置信息 (使用免费API)

    Args:
        ip: IP地址，为空时查询当前IP

    Returns:
        IP地理位置信息
    """
    try:
        # 使用 ipapi.co 的免费API
        if ip:
            url = f"https://ipapi.co/{ip}/json/"
        else:
            url = "https://ipapi.co/json/"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'error' in data:
            return f"❌ 错误: {data['error']}"

        result = f"🌍 IP地理位置信息:\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"🖥️  IP地址: {data.get('ip', 'N/A')}\n"
        result += f"🏙️  城市: {data.get('city', 'N/A')}\n"
        result += f"🏞️  地区: {data.get('region', 'N/A')}\n"
        result += f"🏳️  国家: {data.get('country_name', 'N/A')} ({data.get('country', 'N/A')})\n"
        result += f"📍  坐标: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}\n"
        result += f"🌐  ISP: {data.get('org', 'N/A')}\n"
        result += f"🕒  时区: {data.get('timezone', 'N/A')}\n"

        return result

    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败: {str(e)}"
    except json.JSONDecodeError:
        return f"❌ IP位置数据解析失败"
    except Exception as e:
        return f"❌ 获取IP位置信息失败: {str(e)}"


@tool
def generate_qr_code(text: str, size: str = "200x200") -> str:
    """生成二维码 (使用免费API)

    Args:
        text: 要生成二维码的文本内容
        size: 二维码尺寸，格式为 "宽x高"，如 "200x200"

    Returns:
        二维码生成结果
    """
    try:
        # 使用 qr-server.com 的免费API
        encoded_text = urllib.parse.quote(text)
        url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}&data={encoded_text}"

        result = f"📱 二维码生成成功:\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"📄  内容: {text}\n"
        result += f"📐  尺寸: {size}\n"
        result += f"🔗  二维码链接: {url}\n"
        result += f"💡  使用说明: 复制上面的链接到浏览器查看或下载二维码图片\n"

        return result

    except Exception as e:
        return f"❌ 生成二维码失败: {str(e)}"


@tool
def get_random_joke() -> str:
    """获取随机笑话 (使用免费API)

    Returns:
        随机笑话
    """
    try:
        # 使用 official-joke-api 的免费API
        url = "https://official-joke-api.appspot.com/random_joke"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        result = f"😄 随机笑话:\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"📝  问题: {data.get('setup', 'N/A')}\n"
        result += f"😂  答案: {data.get('punchline', 'N/A')}\n"
        result += f"🏷️  类型: {data.get('type', 'N/A')}\n"

        return result

    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败: {str(e)}"
    except json.JSONDecodeError:
        return f"❌ 笑话数据解析失败"
    except Exception as e:
        return f"❌ 获取笑话失败: {str(e)}"


@tool
def get_random_quote() -> str:
    """获取随机名言 (使用免费API)

    Returns:
        随机名言
    """
    try:
        # 使用 quotable.io 的免费API
        url = "https://api.quotable.io/random"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        result = f"💭 随机名言:\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"📜  内容: \"{data.get('content', 'N/A')}\"\n"
        result += f"👤  作者: {data.get('author', 'N/A')}\n"
        result += f"🏷️  标签: {', '.join(data.get('tags', []))}\n"
        result += f"📏  长度: {data.get('length', 'N/A')} 字符\n"

        return result

    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败: {str(e)}"
    except json.JSONDecodeError:
        return f"❌ 名言数据解析失败"
    except Exception as e:
        return f"❌ 获取名言失败: {str(e)}"


@tool
def shorten_url(long_url: str) -> str:
    """缩短URL (使用免费API)

    Args:
        long_url: 要缩短的长URL

    Returns:
        缩短后的URL
    """
    try:
        # 使用 tinyurl.com 的免费API
        api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        short_url = response.text.strip()

        if short_url.startswith('http'):
            result = f"🔗 URL缩短成功:\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result += f"📎  原URL: {long_url}\n"
            result += f"✂️  短URL: {short_url}\n"
            result += f"📏  节省: {len(long_url) - len(short_url)} 字符\n"

            return result
        else:
            return f"❌ URL缩短失败: {short_url}"

    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败: {str(e)}"
    except Exception as e:
        return f"❌ 缩短URL失败: {str(e)}"


@tool
def get_random_image_url(width: int = 400, height: int = 300, category: str = "") -> str:
    """获取随机图片URL (使用免费API)

    Args:
        width: 图片宽度
        height: 图片高度
        category: 图片类别 (如 nature, city, people, animals)

    Returns:
        随机图片信息
    """
    try:
        # 使用 picsum.photos 的免费API
        if category:
            # 使用 unsplash.com 的免费API
            url = f"https://source.unsplash.com/{width}x{height}/?{category}"
        else:
            # 使用 picsum.photos 的免费API
            url = f"https://picsum.photos/{width}/{height}"

        result = f"🖼️ 随机图片:\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"📐  尺寸: {width}x{height}\n"
        result += f"🏷️  类别: {category if category else '随机'}\n"
        result += f"🔗  图片链接: {url}\n"
        result += f"💡  使用说明: 复制上面的链接到浏览器查看图片\n"

        return result

    except Exception as e:
        return f"❌ 获取随机图片失败: {str(e)}"
