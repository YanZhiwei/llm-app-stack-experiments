# 原有工具
from .calculator_tool import calculate_math

# 新增工具
from .content_generator_tool import generate_detailed_content
from .datetime_tool import (
    add_days_to_date,
    calculate_date_difference,
    get_calendar_info,
    get_current_time,
)
from .flight_tool import get_airport_info, get_flight_price_alert, search_flights
from .logging_tool import (
    clear_logs,
    export_logs_json,
    get_current_session_info,
    get_reasoning_summary,
    get_tool_performance_report,
)
from .markdown_tool import (
    create_business_trip_report,
    create_enhanced_markdown_table,
    create_markdown_report,
    create_markdown_table,
    create_text_chart,
    format_markdown_content,
)
from .memory_tool import retrieve_memory, store_memory
from .online_api_tool import (
    generate_qr_code,
    get_exchange_rate,
    get_ip_location,
    get_random_image_url,
    get_random_joke,
    get_random_quote,
    get_weather_info,
    shorten_url,
)
from .random_generator_tool import (
    generate_password,
    generate_random_choice,
    generate_random_date,
    generate_random_numbers,
    generate_random_text,
    generate_uuid,
)
from .reasoning_tool import analyze_problem
from .search_tool import search_information
from .text_processing_tool import (
    analyze_text,
    extract_patterns,
    format_text,
    text_similarity,
)
from .tool_resolver import resolve_params, resolve_tool_name
from .unit_converter_tool import (
    convert_area,
    convert_length,
    convert_speed,
    convert_temperature,
    convert_volume,
    convert_weight,
)
from .verification_tool import verify_answer


def get_react_tools():
    """获取所有ReAct推理工具"""
    return [
        # 原有核心工具
        search_information,
        calculate_math,
        analyze_problem,
        store_memory,
        retrieve_memory,
        verify_answer,

        # 内容生成工具
        generate_detailed_content,

        # 日期时间工具
        get_current_time,
        calculate_date_difference,
        get_calendar_info,
        add_days_to_date,

        # 文本处理工具
        analyze_text,
        format_text,
        extract_patterns,
        text_similarity,

        # Markdown工具
        create_markdown_report,
        create_markdown_table,
        format_markdown_content,
        create_business_trip_report,
        create_enhanced_markdown_table,
        create_text_chart,

        # 单位转换工具
        convert_length,
        convert_weight,
        convert_temperature,
        convert_area,
        convert_volume,
        convert_speed,

        # 在线API工具
        get_weather_info,
        get_exchange_rate,
        get_ip_location,
        generate_qr_code,
        get_random_joke,
        get_random_quote,
        shorten_url,
        get_random_image_url,

        # 航班工具
        search_flights,
        get_airport_info,
        get_flight_price_alert,

        # 随机生成工具
        generate_password,
        generate_random_numbers,
        generate_uuid,
        generate_random_text,
        generate_random_choice,
        generate_random_date,

        # 日志分析工具
        get_reasoning_summary,
        get_tool_performance_report,
        get_current_session_info,
        export_logs_json,
        clear_logs,
    ]


def get_tool_categories():
    """获取工具分类信息"""
    return {
        "核心工具": [
            "search_information - 搜索信息",
            "calculate_math - 数学计算",
            "analyze_problem - 问题分析",
            "store_memory - 存储记忆",
            "retrieve_memory - 检索记忆",
            "verify_answer - 验证答案",
            "generate_detailed_content - 基于源材料生成详细结构化内容"
        ],
        "日期时间": [
            "get_current_time - 获取当前时间",
            "calculate_date_difference - 计算日期差异",
            "get_calendar_info - 获取日历信息",
            "add_days_to_date - 日期计算"
        ],
        "文本处理": [
            "analyze_text - 文本分析",
            "format_text - 文本格式化",
            "extract_patterns - 模式提取",
            "text_similarity - 文本相似度"
        ],
        "Markdown工具": [
            "create_markdown_report - 创建Markdown报告",
            "create_markdown_table - 创建Markdown表格",
            "format_markdown_content - 格式化Markdown内容",
            "create_business_trip_report - 创建专业商务出差报告",
            "create_enhanced_markdown_table - 创建增强版Markdown表格",
            "create_text_chart - 创建文本图表"
        ],
        "单位转换": [
            "convert_length - 长度转换",
            "convert_weight - 重量转换",
            "convert_temperature - 温度转换",
            "convert_area - 面积转换",
            "convert_volume - 体积转换",
            "convert_speed - 速度转换"
        ],
        "在线API": [
            "get_weather_info - 天气信息",
            "get_exchange_rate - 汇率信息",
            "get_ip_location - IP位置",
            "generate_qr_code - 二维码生成",
            "get_random_joke - 随机笑话",
            "get_random_quote - 随机名言",
            "shorten_url - 短链接",
            "get_random_image_url - 随机图片"
        ],
        "航班工具": [
            "search_flights - 航班查询",
            "get_airport_info - 机场信息",
            "get_flight_price_alert - 价格提醒"
        ],
        "随机生成": [
            "generate_password - 密码生成",
            "generate_random_numbers - 随机数字",
            "generate_uuid - UUID生成",
            "generate_random_text - 随机文本",
            "generate_random_choice - 随机选择",
            "generate_random_date - 随机日期"
        ],
        "日志分析": [
            "get_reasoning_summary - 推理总结",
            "get_tool_performance_report - 工具性能报告",
            "get_current_session_info - 当前会话信息",
            "export_logs_json - 导出日志",
            "clear_logs - 清除日志"
        ]
    }
