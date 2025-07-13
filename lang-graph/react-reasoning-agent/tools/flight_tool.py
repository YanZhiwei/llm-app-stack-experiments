"""
航班查询工具 - 支持模拟和真实API查询
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from langchain_core.tools import tool


@tool
def search_flights(
    departure: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    use_mock: bool = True
) -> Dict[str, Any]:
    """查询航班信息

    Args:
        departure: 出发城市或机场代码
        destination: 目的地城市或机场代码
        departure_date: 出发日期 (YYYY-MM-DD格式)
        return_date: 返程日期 (YYYY-MM-DD格式)，可选
        passengers: 乘客数量，默认1
        use_mock: 是否使用模拟数据，默认True

    Returns:
        包含航班信息的字典，格式为:
        {
            "status": "success" | "error",
            "message": str,
            "search_info": dict,
            "flights": List[dict],
            "total_results": int,
            "search_time": str
        }
    """
    try:
        # 验证输入
        if not departure or not destination:
            return {
                "status": "error",
                "message": "出发地和目的地不能为空",
                "search_info": {},
                "flights": [],
                "total_results": 0,
                "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # 验证日期格式
        try:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        except ValueError:
            return {
                "status": "error",
                "message": "出发日期格式错误，请使用YYYY-MM-DD格式",
                "search_info": {},
                "flights": [],
                "total_results": 0,
                "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        search_info = {
            "departure": departure,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers,
            "trip_type": "round-trip" if return_date else "one-way"
        }

        if use_mock:
            # 使用模拟数据
            flights = _generate_mock_flights(
                departure, destination, departure_date, return_date, passengers)
        else:
            # 使用真实API（需要API密钥）
            flights = _search_real_flights(
                departure, destination, departure_date, return_date, passengers)

        return {
            "status": "success",
            "message": f"成功查询到{len(flights)}个航班",
            "search_info": search_info,
            "flights": flights,
            "total_results": len(flights),
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"航班查询失败: {str(e)}",
            "search_info": {},
            "flights": [],
            "total_results": 0,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def _generate_mock_flights(departure: str, destination: str, departure_date: str, return_date: Optional[str], passengers: int) -> List[Dict[str, Any]]:
    """生成模拟航班数据"""

    # 常见航空公司
    airlines = [
        {"code": "CA", "name": "中国国际航空", "logo": "🇨🇳"},
        {"code": "MU", "name": "中国东方航空", "logo": "🇨🇳"},
        {"code": "CZ", "name": "中国南方航空", "logo": "🇨🇳"},
        {"code": "UA", "name": "美国联合航空", "logo": "🇺🇸"},
        {"code": "DL", "name": "达美航空", "logo": "🇺🇸"},
        {"code": "AA", "name": "美国航空", "logo": "🇺🇸"},
        {"code": "BA", "name": "英国航空", "logo": "🇬🇧"},
        {"code": "LH", "name": "汉莎航空", "logo": "🇩🇪"},
        {"code": "AF", "name": "法国航空", "logo": "🇫🇷"},
        {"code": "KL", "name": "荷兰皇家航空", "logo": "🇳🇱"}
    ]

    # 根据路线调整基础价格
    route_prices = {
        ("上海", "纽约"): {"economy": 1200, "business": 4500, "first": 8000},
        ("上海", "洛杉矶"): {"economy": 1100, "business": 4200, "first": 7500},
        ("北京", "纽约"): {"economy": 1300, "business": 4800, "first": 8500},
        ("北京", "洛杉矶"): {"economy": 1250, "business": 4600, "first": 8200},
        ("广州", "纽约"): {"economy": 1400, "business": 5000, "first": 9000},
        ("上海", "伦敦"): {"economy": 800, "business": 3200, "first": 6000},
        ("上海", "巴黎"): {"economy": 850, "business": 3400, "first": 6200},
        ("上海", "东京"): {"economy": 300, "business": 1200, "first": 2500},
        ("上海", "首尔"): {"economy": 250, "business": 1000, "first": 2000},
        ("北京", "东京"): {"economy": 280, "business": 1100, "first": 2200},
    }

    # 获取基础价格
    base_prices = route_prices.get((departure, destination), {
                                   "economy": 500, "business": 2000, "first": 4000})

    flights = []
    dep_date = datetime.strptime(departure_date, "%Y-%m-%d")

    # 生成3-8个航班
    for i in range(random.randint(3, 8)):
        airline = random.choice(airlines)
        flight_number = f"{airline['code']}{random.randint(100, 999)}"

        # 随机起飞时间
        dep_time = dep_date + \
            timedelta(hours=random.randint(6, 23),
                      minutes=random.choice([0, 15, 30, 45]))

        # 随机飞行时长（根据距离调整）
        if any(dest in ["纽约", "洛杉矶", "芝加哥"] for dest in [departure, destination]):
            flight_duration = random.randint(12, 16)  # 跨太平洋
        elif any(dest in ["伦敦", "巴黎", "法兰克福"] for dest in [departure, destination]):
            flight_duration = random.randint(10, 14)  # 跨欧亚
        elif any(dest in ["东京", "首尔", "大阪"] for dest in [departure, destination]):
            flight_duration = random.randint(2, 4)    # 东亚
        else:
            flight_duration = random.randint(1, 12)   # 其他

        arr_time = dep_time + timedelta(hours=flight_duration)

        # 生成舱位和价格
        classes = []
        for class_type, base_price in base_prices.items():
            # 价格浮动 ±20%
            price_variation = random.uniform(0.8, 1.2)
            price = int(base_price * price_variation)

            # 剩余座位
            remaining_seats = random.randint(0, 50)

            classes.append({
                "class": class_type,
                "class_name": {"economy": "经济舱", "business": "商务舱", "first": "头等舱"}[class_type],
                "price": price,
                "currency": "USD",
                "remaining_seats": remaining_seats,
                "available": remaining_seats > 0
            })

        # 随机中转
        is_direct = random.choice([True, True, False])  # 2/3概率直飞
        stopovers = []
        if not is_direct:
            stopover_cities = ["东京", "首尔", "香港", "新加坡", "迪拜", "法兰克福", "阿姆斯特丹"]
            stopover = random.choice(stopover_cities)
            stopovers.append({
                "city": stopover,
                "duration": f"{random.randint(1, 5)}小时{random.randint(0, 59)}分钟"
            })

        flight = {
            "flight_number": flight_number,
            "airline": airline,
            "departure": {
                "city": departure,
                "airport": f"{departure}机场",
                "time": dep_time.strftime("%Y-%m-%d %H:%M"),
                "terminal": random.choice(["T1", "T2", "T3"])
            },
            "arrival": {
                "city": destination,
                "airport": f"{destination}机场",
                "time": arr_time.strftime("%Y-%m-%d %H:%M"),
                "terminal": random.choice(["T1", "T2", "T3"])
            },
            "duration": f"{flight_duration}小时{random.randint(0, 59)}分钟",
            "aircraft": random.choice(["Boeing 777", "Boeing 787", "Airbus A350", "Airbus A380", "Boeing 747"]),
            "is_direct": is_direct,
            "stopovers": stopovers,
            "classes": classes,
            "services": {
                "wifi": random.choice([True, False]),
                "meal": random.choice([True, False]),
                "entertainment": random.choice([True, False])
            }
        }

        flights.append(flight)

    # 按价格排序
    flights.sort(key=lambda x: x["classes"][0]["price"])

    return flights


def _search_real_flights(departure: str, destination: str, departure_date: str, return_date: Optional[str], passengers: int) -> List[Dict[str, Any]]:
    """使用真实API查询航班（需要API密钥）"""

    # 这里可以集成真实的航班API
    # 1. Amadeus API (需要注册免费账号)
    # 2. RapidAPI上的航班API
    # 3. AviationStack API

    # 示例：使用Amadeus API
    try:
        # 注意：这需要真实的API密钥
        # amadeus_api_key = "YOUR_AMADEUS_API_KEY"
        # amadeus_api_secret = "YOUR_AMADEUS_API_SECRET"

        # 这里只是示例代码，实际需要配置API密钥
        # url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        # params = {
        #     "originLocationCode": _get_airport_code(departure),
        #     "destinationLocationCode": _get_airport_code(destination),
        #     "departureDate": departure_date,
        #     "adults": passengers
        # }
        # if return_date:
        #     params["returnDate"] = return_date

        # response = requests.get(url, params=params, headers={
        #     "Authorization": f"Bearer {amadeus_access_token}"
        # })

        # 目前返回空列表，提示需要配置API
        return [{
            "flight_number": "API_NEEDED",
            "airline": {"code": "XX", "name": "请配置真实API", "logo": "⚠️"},
            "departure": {"city": departure, "time": "需要API密钥"},
            "arrival": {"city": destination, "time": "需要API密钥"},
            "duration": "需要配置API",
            "classes": [{"class": "economy", "price": 0, "currency": "USD"}],
            "note": "请在代码中配置真实的航班API密钥"
        }]

    except Exception as e:
        print(f"真实API调用失败: {e}")
        return []


def _get_airport_code(city: str) -> str:
    """获取城市对应的机场代码"""
    airport_codes = {
        "上海": "SHA",
        "北京": "PEK",
        "广州": "CAN",
        "深圳": "SZX",
        "纽约": "JFK",
        "洛杉矶": "LAX",
        "芝加哥": "ORD",
        "伦敦": "LHR",
        "巴黎": "CDG",
        "法兰克福": "FRA",
        "东京": "NRT",
        "首尔": "ICN",
        "香港": "HKG",
        "新加坡": "SIN",
        "迪拜": "DXB"
    }
    return airport_codes.get(city, city)


@tool
def get_flight_price_alert(
    departure: str,
    destination: str,
    departure_date: str,
    max_price: float,
    currency: str = "USD"
) -> Dict[str, Any]:
    """设置航班价格提醒

    Args:
        departure: 出发城市
        destination: 目的地城市
        departure_date: 出发日期
        max_price: 最高价格
        currency: 货币单位

    Returns:
        价格提醒设置结果
    """
    try:
        alert_id = f"alert_{random.randint(1000, 9999)}"

        return {
            "status": "success",
            "message": f"价格提醒设置成功，当{departure}到{destination}的航班价格低于{max_price}{currency}时将通知您",
            "alert_id": alert_id,
            "alert_info": {
                "departure": departure,
                "destination": destination,
                "departure_date": departure_date,
                "max_price": max_price,
                "currency": currency,
                "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"设置价格提醒失败: {str(e)}",
            "alert_id": "",
            "alert_info": {}
        }


@tool
def get_airport_info(airport_code: str) -> Dict[str, Any]:
    """获取机场信息

    Args:
        airport_code: 机场代码或城市名称

    Returns:
        机场信息字典
    """
    try:
        # 机场信息数据库
        airport_info = {
            "SHA": {
                "name": "上海浦东国际机场",
                "city": "上海",
                "country": "中国",
                "iata": "SHA",
                "icao": "ZSPD",
                "timezone": "Asia/Shanghai",
                "terminals": ["T1", "T2"],
                "facilities": ["免税店", "餐厅", "Wi-Fi", "休息室", "银行", "医疗服务"]
            },
            "PEK": {
                "name": "北京首都国际机场",
                "city": "北京",
                "country": "中国",
                "iata": "PEK",
                "icao": "ZBAA",
                "timezone": "Asia/Shanghai",
                "terminals": ["T1", "T2", "T3"],
                "facilities": ["免税店", "餐厅", "Wi-Fi", "休息室", "银行", "医疗服务", "酒店"]
            },
            "JFK": {
                "name": "约翰·肯尼迪国际机场",
                "city": "纽约",
                "country": "美国",
                "iata": "JFK",
                "icao": "KJFK",
                "timezone": "America/New_York",
                "terminals": ["T1", "T2", "T4", "T5", "T7", "T8"],
                "facilities": ["免税店", "餐厅", "Wi-Fi", "休息室", "银行", "医疗服务", "酒店", "会议室"]
            },
            "LAX": {
                "name": "洛杉矶国际机场",
                "city": "洛杉矶",
                "country": "美国",
                "iata": "LAX",
                "icao": "KLAX",
                "timezone": "America/Los_Angeles",
                "terminals": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "TBIT"],
                "facilities": ["免税店", "餐厅", "Wi-Fi", "休息室", "银行", "医疗服务", "酒店"]
            }
        }

        # 尝试直接匹配机场代码
        if airport_code.upper() in airport_info:
            info = airport_info[airport_code.upper()]
        else:
            # 尝试通过城市名称匹配
            city_code = _get_airport_code(airport_code)
            if city_code in airport_info:
                info = airport_info[city_code]
            else:
                return {
                    "status": "error",
                    "message": f"未找到机场信息: {airport_code}",
                    "airport_info": {}
                }

        return {
            "status": "success",
            "message": f"成功获取{info['name']}信息",
            "airport_info": info
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取机场信息失败: {str(e)}",
            "airport_info": {}
        }
