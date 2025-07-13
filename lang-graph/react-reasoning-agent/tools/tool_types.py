from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


class BaseToolResponse(TypedDict):
    """所有工具的基础响应格式"""
    status: Literal["success", "error"]
    message: str

# 日期时间工具


class GetCurrentTimeInput(TypedDict):
    format_type: Literal["complete", "date", "time", "timestamp"]


class GetCurrentTimeOutput(BaseToolResponse):
    date: str
    weekday: str
    time: str
    timestamp: float
    iso_format: str


class DateDifferenceInput(TypedDict):
    date1: str  # YYYY-MM-DD
    date2: Optional[str]  # YYYY-MM-DD, optional


class DateDifferenceOutput(BaseToolResponse):
    days: int
    weeks: int
    months: int
    years: float
    is_future: bool

# 计算器工具


class CalculatorInput(TypedDict):
    expression: str
    precision: Optional[int]  # 默认2位小数


class CalculatorOutput(BaseToolResponse):
    expression: str
    result: float
    formatted_result: str

# 天气工具


class WeatherInput(TypedDict):
    city: str
    country: Optional[str]  # ISO country code, 默认 CN


class WeatherOutput(BaseToolResponse):
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    visibility: float
    pressure: float
    observation_time: str

# 汇率工具


class ExchangeRateInput(TypedDict):
    from_currency: str  # 如 USD, EUR
    to_currency: str    # 如 CNY, JPY


class ExchangeRateOutput(BaseToolResponse):
    rate: float
    base_currency: str
    target_currency: str
    update_time: str
    examples: List[dict]  # 包含示例换算

# 搜索工具


class SearchInput(TypedDict):
    query: str


class SearchOutput(BaseToolResponse):
    query: str
    results: List[str]
    source: str

# 文本处理工具


class TextAnalysisInput(TypedDict):
    text: str


class TextAnalysisOutput(BaseToolResponse):
    char_count: int
    word_count: int
    line_count: int
    paragraph_count: int
    sentence_count: int
    language_features: Dict[str, bool]
    most_common_words: List[Dict[str, Any]]
    readability_metrics: Dict[str, float]


class TextFormatInput(TypedDict):
    text: str
    operation: Literal["upper", "lower", "title", "capitalize", "reverse",
                       "remove_spaces", "snake_case", "camel_case", "kebab_case"]


class TextFormatOutput(BaseToolResponse):
    original_text: str
    formatted_text: str
    operation: str


class PatternExtractInput(TypedDict):
    text: str
    pattern_type: Literal["email", "url", "phone",
                          "number", "chinese", "english", "ip", "date", "time"]


class PatternExtractOutput(BaseToolResponse):
    pattern_type: str
    matches: List[str]
    unique_matches: List[str]
    match_count: int


class TextSimilarityInput(TypedDict):
    text1: str
    text2: str


class TextSimilarityOutput(BaseToolResponse):
    char_similarity: float
    word_similarity: float
    length_ratio: float
    overall_similarity: float

# 内存工具


class MemoryStoreInput(TypedDict):
    key: str
    value: str


class MemoryStoreOutput(BaseToolResponse):
    key: str
    value: str
    total_memories: int


class MemoryRetrieveInput(TypedDict):
    key: Optional[str]  # 为空时返回所有记忆


class MemoryRetrieveOutput(BaseToolResponse):
    key: Optional[str]
    memories: List[Dict[str, str]]
    total_count: int

# 单位转换工具


class UnitConvertInput(TypedDict):
    value: float
    from_unit: str
    to_unit: str


class UnitConvertOutput(BaseToolResponse):
    original_value: float
    converted_value: float
    from_unit: str
    to_unit: str
    conversion_factor: float

# 随机生成工具


class RandomPasswordInput(TypedDict):
    length: Optional[int]
    include_symbols: Optional[bool]
    include_numbers: Optional[bool]
    include_uppercase: Optional[bool]


class RandomPasswordOutput(BaseToolResponse):
    password: str
    length: int
    character_types: List[str]


class RandomNumbersInput(TypedDict):
    count: Optional[int]
    min_value: Optional[int]
    max_value: Optional[int]


class RandomNumbersOutput(BaseToolResponse):
    numbers: List[int]
    count: int
    range_info: Dict[str, int]

# 推理工具


class ProblemAnalysisInput(TypedDict):
    problem: str


class ProblemAnalysisOutput(BaseToolResponse):
    problem: str
    analysis: str
    steps: List[str]
    complexity: Literal["simple", "medium", "complex"]
    estimated_time: str

# 验证工具


class VerificationInput(TypedDict):
    question: str
    answer: str


class VerificationOutput(BaseToolResponse):
    question: str
    answer: str
    is_correct: bool
    confidence: float
    explanation: str


# 日志工具类型
class LogReasoningInput(TypedDict):
    step_type: str
    content: str
    iteration: int


class LogReasoningOutput(BaseToolResponse):
    step_type: str
    content: str
    iteration: int
    timestamp: str


class LogToolUsageInput(TypedDict):
    tool_name: str
    tool_args: Dict[str, Any]
    execution_time: float
    result_summary: str


class LogToolUsageOutput(BaseToolResponse):
    tool_name: str
    execution_time: float
    success: bool
    timestamp: str


class LogSummaryOutput(BaseToolResponse):
    total_reasoning_steps: int
    total_tool_calls: int
    total_execution_time: float
    iterations: List[Dict[str, Any]]
    tool_statistics: Dict[str, Dict[str, Any]]


class LogPerformanceOutput(BaseToolResponse):
    total_calls: int
    success_rate: float
    average_execution_time: float
    fastest_execution: float
    slowest_execution: float
    tool_rankings: List[Dict[str, Any]]


class LogExportOutput(BaseToolResponse):
    export_time: str
    reasoning_logs: List[Dict[str, Any]]
    tool_usage_logs: List[Dict[str, Any]]
    summary: Dict[str, Any]
