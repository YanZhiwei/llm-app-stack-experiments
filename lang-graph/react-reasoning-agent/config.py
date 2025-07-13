"""
ReAct推理系统配置文件
统一管理所有系统参数
"""

# 推理系统配置


class ReActConfig:
    """ReAct推理系统配置"""

    # 默认最大迭代次数
    DEFAULT_MAX_ITERATIONS = 6

    # 不同策略的最大迭代次数配置
    STRATEGY_MAX_ITERATIONS = {
        "sequential": 6,     # 顺序推理（增加到6轮确保文件生成）
        "parallel": 4,       # 并行推理（增加到4轮）
        "hierarchical": 8,   # 层次推理（增加到8轮，复杂问题需要更多轮次）
        "adaptive": 10,      # 自适应推理（增加到10轮，最灵活）
        "focused": 5,        # 聚焦推理（增加到5轮）
        "exploratory": 12    # 探索推理（增加到12轮，最多轮次）
    }

    # 推理系统其他配置
    CONFIDENCE_THRESHOLD = 0.8
    PROGRESS_THRESHOLD = 0.3

    # 迭代次数管理策略
    AUTO_ADJUST_ITERATIONS = True  # 是否根据推理策略自动调整迭代次数
    DYNAMIC_ITERATION_EXTENSION = True  # 是否允许动态扩展迭代次数（检测到复杂任务时）
    MAX_DYNAMIC_ITERATIONS = 15  # 动态调整时的最大迭代次数上限

    # 🆕 迭代次数控制模式
    # 控制模式：strict(严格限制) / intelligent(智能调整) / flexible(灵活限制)
    ITERATION_CONTROL_MODE = "intelligent"

    # 不同模式的行为说明：
    # - strict: 严格按照策略限制，不允许超出
    # - intelligent: 基于任务完成度智能调整，允许根据实际需要扩展
    # - flexible: 只有安全上限，主要依赖LLM判断任务完成

    # 智能调整模式的配置
    INTELLIGENT_ADJUSTMENT_CONFIG = {
        "base_iterations": 6,  # 基础迭代次数
        "max_safe_iterations": 40,  # 安全上限
        "completion_confidence_threshold": 0.9,  # 任务完成信心度阈值
        "progress_stagnation_threshold": 3,  # 进展停滞检测轮次
        "auto_extension_conditions": [
            "file_generation_required",  # 需要文件生成
            "complex_calculation_required",  # 需要复杂计算
            "multi_step_verification_required"  # 需要多步验证
        ]
    }

    # 工具配置
    TOOL_LIMIT = 39
    MIN_TOOL_DIVERSITY = 3

    # 调试配置
    DEBUG_MODE = False
    VERBOSE_LOGGING = True

    # 结果质量评估配置
    ENABLE_RESULT_QUALITY_ASSESSMENT = True  # 是否启用结果质量评估
    QUALITY_ASSESSMENT_THRESHOLD = 7.0  # 质量评分阈值，低于此分数会提供额外建议


# 全局配置实例
config = ReActConfig()
