"""
MCP工具适配器 - 处理新旧工具格式的转换
"""
import json
from typing import Any, Dict, List, Optional, Union

from .tool_types import BaseToolResponse


class MCPToolAdapter:
    """MCP工具适配器，用于统一处理工具调用"""

    def __init__(self):
        self.tool_schemas = {
            "get_current_time": {
                "name": "get_current_time",
                "description": "获取当前时间信息",
                "parameters": {
                    "format_type": {
                        "type": "string",
                        "enum": ["complete", "date", "time", "timestamp"],
                        "default": "complete",
                        "description": "时间格式类型"
                    }
                },
                "required": ["format_type"]
            },
            "calculate_date_difference": {
                "name": "calculate_date_difference",
                "description": "计算两个日期之间的差异",
                "parameters": {
                    "date1": {
                        "type": "string",
                        "description": "第一个日期 (YYYY-MM-DD格式)"
                    },
                    "date2": {
                        "type": "string",
                        "description": "第二个日期 (YYYY-MM-DD格式)，可选，默认为当前日期",
                        "default": ""
                    }
                },
                "required": ["date1"]
            },
            "calculate_math": {
                "name": "calculate_math",
                "description": "执行数学计算",
                "parameters": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式"
                    },
                    "precision": {
                        "type": "integer",
                        "description": "保留小数位数",
                        "default": 2
                    }
                },
                "required": ["expression"]
            },
            "get_weather_info": {
                "name": "get_weather_info",
                "description": "获取天气信息",
                "parameters": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "country": {
                        "type": "string",
                        "description": "国家代码",
                        "default": "CN"
                    }
                },
                "required": ["city"]
            },
            "get_exchange_rate": {
                "name": "get_exchange_rate",
                "description": "获取汇率信息",
                "parameters": {
                    "from_currency": {
                        "type": "string",
                        "description": "源货币代码 (如 USD, EUR)"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "目标货币代码 (如 CNY, JPY)"
                    }
                },
                "required": ["from_currency", "to_currency"]
            },

            # 单位转换工具
            "convert_length": {
                "name": "convert_length",
                "description": "长度单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (mm, cm, m, km, inch, ft, yard, mile)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (mm, cm, m, km, inch, ft, yard, mile)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            "convert_temperature": {
                "name": "convert_temperature",
                "description": "温度单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (C, F, K)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (C, F, K)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            # 随机生成工具
            "generate_password": {
                "name": "generate_password",
                "description": "生成随机密码",
                "parameters": {
                    "length": {
                        "type": "integer",
                        "description": "密码长度",
                        "default": 12
                    },
                    "include_symbols": {
                        "type": "boolean",
                        "description": "是否包含特殊字符",
                        "default": True
                    }
                },
                "required": []
            },

            "generate_random_numbers": {
                "name": "generate_random_numbers",
                "description": "生成随机数",
                "parameters": {
                    "count": {
                        "type": "integer",
                        "description": "生成数量",
                        "default": 5
                    },
                    "min_value": {
                        "type": "integer",
                        "description": "最小值",
                        "default": 1
                    },
                    "max_value": {
                        "type": "integer",
                        "description": "最大值",
                        "default": 100
                    }
                },
                "required": []
            },

            # 核心工具
            "search_information": {
                "name": "search_information",
                "description": "搜索相关信息",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询字符串"
                    }
                },
                "required": ["query"]
            },

            "analyze_problem": {
                "name": "analyze_problem",
                "description": "分析问题并提供推理建议",
                "parameters": {
                    "problem": {
                        "type": "string",
                        "description": "需要分析的问题描述"
                    }
                },
                "required": ["problem"]
            },

            "store_memory": {
                "name": "store_memory",
                "description": "存储信息到记忆中",
                "parameters": {
                    "key": {
                        "type": "string",
                        "description": "信息的关键词或标题"
                    },
                    "value": {
                        "type": "string",
                        "description": "要存储的信息内容"
                    }
                },
                "required": ["key", "value"]
            },

            "retrieve_memory": {
                "name": "retrieve_memory",
                "description": "从记忆中检索信息",
                "parameters": {
                    "key": {
                        "type": "string",
                        "description": "要检索的信息关键词",
                        "default": ""
                    }
                },
                "required": []
            },

            "verify_answer": {
                "name": "verify_answer",
                "description": "验证答案的正确性",
                "parameters": {
                    "question": {
                        "type": "string",
                        "description": "原始问题"
                    },
                    "answer": {
                        "type": "string",
                        "description": "待验证的答案"
                    },
                    "context": {
                        "type": "string",
                        "description": "相关上下文信息",
                        "default": ""
                    }
                },
                "required": ["question", "answer"]
            },

            # 日期时间工具
            "get_calendar_info": {
                "name": "get_calendar_info",
                "description": "获取日历信息",
                "parameters": {
                    "year": {
                        "type": "integer",
                        "description": "年份",
                        "default": 0
                    },
                    "month": {
                        "type": "integer",
                        "description": "月份",
                        "default": 0
                    }
                },
                "required": []
            },

            "add_days_to_date": {
                "name": "add_days_to_date",
                "description": "在指定日期上增加天数",
                "parameters": {
                    "date": {
                        "type": "string",
                        "description": "基准日期 (YYYY-MM-DD格式)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "要增加的天数"
                    }
                },
                "required": ["date", "days"]
            },

            # 文本处理工具
            "analyze_text": {
                "name": "analyze_text",
                "description": "分析文本内容",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "要分析的文本内容"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "分析类型",
                        "enum": ["basic", "sentiment", "keywords", "summary"],
                        "default": "basic"
                    }
                },
                "required": ["text"]
            },

            "format_text": {
                "name": "format_text",
                "description": "格式化文本",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "要格式化的文本"
                    },
                    "format_type": {
                        "type": "string",
                        "description": "格式化类型",
                        "enum": ["uppercase", "lowercase", "title", "sentence", "clean"],
                        "default": "clean"
                    }
                },
                "required": ["text"]
            },

            "extract_patterns": {
                "name": "extract_patterns",
                "description": "从文本中提取模式",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "要分析的文本"
                    },
                    "pattern_type": {
                        "type": "string",
                        "description": "模式类型",
                        "enum": ["email", "phone", "url", "number", "date"],
                        "default": "email"
                    }
                },
                "required": ["text"]
            },

            "text_similarity": {
                "name": "text_similarity",
                "description": "计算文本相似度",
                "parameters": {
                    "text1": {
                        "type": "string",
                        "description": "第一个文本"
                    },
                    "text2": {
                        "type": "string",
                        "description": "第二个文本"
                    },
                    "method": {
                        "type": "string",
                        "description": "相似度计算方法",
                        "enum": ["jaccard", "cosine", "levenshtein"],
                        "default": "jaccard"
                    }
                },
                "required": ["text1", "text2"]
            },

            # 更多单位转换工具
            "convert_weight": {
                "name": "convert_weight",
                "description": "重量单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (g, kg, lb, oz, ton)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (g, kg, lb, oz, ton)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            "convert_area": {
                "name": "convert_area",
                "description": "面积单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (sqm, sqft, acre, hectare)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (sqm, sqft, acre, hectare)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            "convert_volume": {
                "name": "convert_volume",
                "description": "体积单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (ml, l, gallon, quart, pint, cup)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (ml, l, gallon, quart, pint, cup)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            "convert_speed": {
                "name": "convert_speed",
                "description": "速度单位转换",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "数值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "原单位 (mps, kmh, mph, knot)"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标单位 (mps, kmh, mph, knot)"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },

            # 在线API工具
            "get_ip_location": {
                "name": "get_ip_location",
                "description": "获取IP地址位置信息",
                "parameters": {
                    "ip": {
                        "type": "string",
                        "description": "IP地址，留空则获取当前IP",
                        "default": ""
                    }
                },
                "required": []
            },

            # 航班工具
            "search_flights": {
                "name": "search_flights",
                "description": "查询航班信息",
                "parameters": {
                    "departure": {
                        "type": "string",
                        "description": "出发城市或机场代码"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地城市或机场代码"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "出发日期 (YYYY-MM-DD格式)"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "返程日期 (YYYY-MM-DD格式)，可选",
                        "default": ""
                    },
                    "passengers": {
                        "type": "integer",
                        "description": "乘客数量",
                        "default": 1
                    },
                    "use_mock": {
                        "type": "boolean",
                        "description": "是否使用模拟数据",
                        "default": True
                    }
                },
                "required": ["departure", "destination", "departure_date"]
            },

            "get_airport_info": {
                "name": "get_airport_info",
                "description": "获取机场信息",
                "parameters": {
                    "airport_code": {
                        "type": "string",
                        "description": "机场代码或城市名称"
                    }
                },
                "required": ["airport_code"]
            },

            "get_flight_price_alert": {
                "name": "get_flight_price_alert",
                "description": "设置航班价格提醒",
                "parameters": {
                    "departure": {
                        "type": "string",
                        "description": "出发城市"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地城市"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "出发日期 (YYYY-MM-DD格式)"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "最高价格"
                    },
                    "currency": {
                        "type": "string",
                        "description": "货币单位",
                        "default": "USD"
                    }
                },
                "required": ["departure", "destination", "departure_date", "max_price"]
            },

            "generate_qr_code": {
                "name": "generate_qr_code",
                "description": "生成二维码",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "要编码的文本"
                    },
                    "size": {
                        "type": "string",
                        "description": "二维码尺寸",
                        "enum": ["small", "medium", "large"],
                        "default": "medium"
                    }
                },
                "required": ["text"]
            },

            "get_random_joke": {
                "name": "get_random_joke",
                "description": "获取随机笑话",
                "parameters": {
                    "category": {
                        "type": "string",
                        "description": "笑话类别",
                        "enum": ["general", "programming", "dad", "pun"],
                        "default": "general"
                    }
                },
                "required": []
            },

            "get_random_quote": {
                "name": "get_random_quote",
                "description": "获取随机名言",
                "parameters": {
                    "category": {
                        "type": "string",
                        "description": "名言类别",
                        "enum": ["motivational", "life", "success", "wisdom"],
                        "default": "motivational"
                    }
                },
                "required": []
            },

            "shorten_url": {
                "name": "shorten_url",
                "description": "缩短URL",
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "要缩短的URL"
                    }
                },
                "required": ["url"]
            },

            "get_random_image_url": {
                "name": "get_random_image_url",
                "description": "获取随机图片URL",
                "parameters": {
                    "category": {
                        "type": "string",
                        "description": "图片类别",
                        "enum": ["nature", "technology", "abstract", "animals"],
                        "default": "nature"
                    },
                    "size": {
                        "type": "string",
                        "description": "图片尺寸",
                        "enum": ["small", "medium", "large"],
                        "default": "medium"
                    }
                },
                "required": []
            },

            # 更多随机生成工具
            "generate_uuid": {
                "name": "generate_uuid",
                "description": "生成UUID",
                "parameters": {
                    "version": {
                        "type": "integer",
                        "description": "UUID版本",
                        "enum": [1, 4],
                        "default": 4
                    }
                },
                "required": []
            },

            "generate_random_text": {
                "name": "generate_random_text",
                "description": "生成随机文本",
                "parameters": {
                    "length": {
                        "type": "integer",
                        "description": "文本长度",
                        "default": 100
                    },
                    "text_type": {
                        "type": "string",
                        "description": "文本类型",
                        "enum": ["lorem", "words", "sentences"],
                        "default": "words"
                    }
                },
                "required": []
            },

            "generate_random_choice": {
                "name": "generate_random_choice",
                "description": "从选项中随机选择",
                "parameters": {
                    "options": {
                        "type": "string",
                        "description": "选项列表，用逗号分隔"
                    }
                },
                "required": ["options"]
            },

            "generate_random_date": {
                "name": "generate_random_date",
                "description": "生成随机日期",
                "parameters": {
                    "start_date": {
                        "type": "string",
                        "description": "开始日期 (YYYY-MM-DD)",
                        "default": "2020-01-01"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期 (YYYY-MM-DD)",
                        "default": "2025-12-31"
                    }
                },
                "required": []
            },

            # 日志分析工具
            "get_reasoning_summary": {
                "name": "get_reasoning_summary",
                "description": "获取推理过程摘要",
                "parameters": {
                    "format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["text", "json", "markdown"],
                        "default": "text"
                    }
                },
                "required": []
            },

            "get_tool_performance_report": {
                "name": "get_tool_performance_report",
                "description": "获取工具性能报告",
                "parameters": {
                    "tool_name": {
                        "type": "string",
                        "description": "工具名称，留空则获取所有工具",
                        "default": ""
                    }
                },
                "required": []
            },

            "get_current_session_info": {
                "name": "get_current_session_info",
                "description": "获取当前会话信息",
                "parameters": {
                    "include_logs": {
                        "type": "boolean",
                        "description": "是否包含日志信息",
                        "default": False
                    }
                },
                "required": []
            },

            "export_logs_json": {
                "name": "export_logs_json",
                "description": "导出日志为JSON格式",
                "parameters": {
                    "filename": {
                        "type": "string",
                        "description": "输出文件名",
                        "default": "reasoning_logs.json"
                    }
                },
                "required": []
            },

            "clear_logs": {
                "name": "clear_logs",
                "description": "清除日志记录",
                "parameters": {
                    "confirm": {
                        "type": "boolean",
                        "description": "确认清除",
                        "default": False
                    }
                },
                "required": []
            },

            # Markdown工具
            "create_markdown_report": {
                "name": "create_markdown_report",
                "description": "创建markdown报告",
                "parameters": {
                    "title": {
                        "type": "string",
                        "description": "报告标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "报告内容（JSON字符串格式）"
                    },
                    "save_file": {
                        "type": "string",
                        "description": "保存文件名（可选）",
                        "default": ""
                    },
                    "template": {
                        "type": "string",
                        "description": "模板类型",
                        "enum": ["business", "simple", "detailed"],
                        "default": "business"
                    }
                },
                "required": ["title", "content"]
            },

            "create_markdown_table": {
                "name": "create_markdown_table",
                "description": "创建markdown表格",
                "parameters": {
                    "headers": {
                        "type": "string",
                        "description": "表头列表（JSON字符串格式）"
                    },
                    "rows": {
                        "type": "string",
                        "description": "数据行列表（JSON字符串格式）"
                    },
                    "alignment": {
                        "type": "string",
                        "description": "对齐方式列表（JSON字符串格式）",
                        "default": ""
                    },
                    "caption": {
                        "type": "string",
                        "description": "表格标题",
                        "default": ""
                    }
                },
                "required": ["headers", "rows"]
            },

            "format_markdown_content": {
                "name": "format_markdown_content",
                "description": "格式化markdown内容",
                "parameters": {
                    "content": {
                        "type": "string",
                        "description": "原始内容"
                    },
                    "format_type": {
                        "type": "string",
                        "description": "格式类型",
                        "enum": ["standard", "github", "business"],
                        "default": "standard"
                    },
                    "add_toc": {
                        "type": "boolean",
                        "description": "是否添加目录",
                        "default": False
                    },
                    "add_timestamp": {
                        "type": "boolean",
                        "description": "是否添加时间戳",
                        "default": True
                    }
                },
                "required": ["content"]
            },

            # 增强版Markdown工具
            "create_business_trip_report": {
                "name": "create_business_trip_report",
                "description": "创建专业的商务出差分析报告",
                "parameters": {
                    "title": {
                        "type": "string",
                        "description": "报告标题"
                    },
                    "trip_data": {
                        "type": "string",
                        "description": "出差数据（JSON字符串格式）"
                    },
                    "save_file": {
                        "type": "string",
                        "description": "保存文件名（可选）",
                        "default": ""
                    },
                    "include_charts": {
                        "type": "boolean",
                        "description": "是否包含图表",
                        "default": True
                    },
                    "include_summary": {
                        "type": "boolean",
                        "description": "是否包含执行摘要",
                        "default": True
                    }
                },
                "required": ["title", "trip_data"]
            },

            "create_enhanced_markdown_table": {
                "name": "create_enhanced_markdown_table",
                "description": "创建增强版markdown表格，支持更多样式",
                "parameters": {
                    "headers": {
                        "type": "string",
                        "description": "表头列表（JSON字符串格式）"
                    },
                    "rows": {
                        "type": "string",
                        "description": "数据行列表（JSON字符串格式）"
                    },
                    "table_style": {
                        "type": "string",
                        "description": "表格样式",
                        "enum": ["standard", "colored", "bordered", "compact"],
                        "default": "standard"
                    },
                    "alignment": {
                        "type": "string",
                        "description": "对齐方式列表（JSON字符串格式）",
                        "default": ""
                    },
                    "caption": {
                        "type": "string",
                        "description": "表格标题",
                        "default": ""
                    },
                    "highlight_rows": {
                        "type": "string",
                        "description": "需要高亮的行索引（JSON字符串格式）",
                        "default": ""
                    }
                },
                "required": ["headers", "rows"]
            },

            "create_text_chart": {
                "name": "create_text_chart",
                "description": "创建文本图表（ASCII艺术风格）",
                "parameters": {
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型",
                        "enum": ["bar", "pie", "line"],
                        "default": "bar"
                    },
                    "data": {
                        "type": "string",
                        "description": "数据列表（JSON字符串格式）"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题",
                        "default": ""
                    },
                    "labels": {
                        "type": "string",
                        "description": "数据标签（JSON字符串格式）",
                        "default": ""
                    }
                },
                "required": ["data"]
            },

            "generate_detailed_content": {
                "name": "generate_detailed_content",
                "description": "基于源材料生成详细的结构化内容",
                "parameters": {
                    "topic": {
                        "type": "string",
                        "description": "主题或项目名称"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "内容类型",
                        "enum": ["report", "analysis", "plan", "guide", "proposal", "research"],
                        "default": "report"
                    },
                    "sections": {
                        "type": "string",
                        "description": "需要包含的章节（逗号分隔或JSON格式）",
                        "default": ""
                    },
                    "detail_level": {
                        "type": "string",
                        "description": "详细程度",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "default": "detailed"
                    },
                    "source_materials": {
                        "type": "string",
                        "description": "源材料内容（其他工具的输出结果）",
                        "default": ""
                    },
                    "language": {
                        "type": "string",
                        "description": "语言",
                        "enum": ["chinese", "english"],
                        "default": "chinese"
                    }
                },
                "required": ["topic"]
            }
        }

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具的参数模式"""
        return self.tool_schemas.get(tool_name)

    def get_all_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具的参数模式"""
        return self.tool_schemas

    def validate_tool_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证工具参数并填充默认值"""
        schema = self.get_tool_schema(tool_name)
        if not schema:
            return params

        validated_params = {}
        param_schemas = schema.get("parameters", {})
        required_params = schema.get("required", [])

        # 检查必需参数
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")

        # 验证和填充参数
        for param_name, param_schema in param_schemas.items():
            if param_name in params:
                validated_params[param_name] = params[param_name]
            elif "default" in param_schema:
                validated_params[param_name] = param_schema["default"]

        return validated_params

    def format_tool_response(self, tool_name: str, response: Any) -> Dict[str, Any]:
        """格式化工具响应为统一格式"""
        if isinstance(response, dict) and "status" in response:
            # 已经是MCP格式
            return response
        elif isinstance(response, str):
            # 旧格式的字符串响应
            return {
                "status": "success",
                "message": "执行成功",
                "data": response
            }
        else:
            # 其他格式
            return {
                "status": "success",
                "message": "执行成功",
                "data": str(response)
            }

    def generate_tool_documentation(self) -> str:
        """生成工具文档，供LLM理解"""
        doc = "=== 可用工具列表 ===\n\n"

        for tool_name, schema in self.tool_schemas.items():
            doc += f"🔧 {tool_name}\n"
            doc += f"   描述: {schema['description']}\n"
            doc += f"   参数:\n"

            for param_name, param_info in schema.get("parameters", {}).items():
                required = param_name in schema.get("required", [])
                default = param_info.get("default", "")

                doc += f"     - {param_name} ({param_info['type']})"
                if required:
                    doc += " [必需]"
                if default:
                    doc += f" [默认: {default}]"
                doc += f": {param_info['description']}\n"

            doc += "\n"

        doc += "\n=== 调用格式 ===\n"
        doc += "使用JSON格式调用工具:\n"
        doc += '{\n'
        doc += '  "tool_name": "工具名称",\n'
        doc += '  "parameters": {\n'
        doc += '    "参数名": "参数值"\n'
        doc += '  }\n'
        doc += '}\n\n'

        return doc


# 全局适配器实例
mcp_adapter = MCPToolAdapter()
