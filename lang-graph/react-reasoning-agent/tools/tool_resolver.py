from .param_alias_config import PARAM_ALIASES
from .tool_alias_config import TOOL_ALIASES


def resolve_tool_name(tool_name: str) -> str:
    """
    根据别名表自动映射工具名。
    """
    return TOOL_ALIASES.get(tool_name, tool_name)


def resolve_params(tool_name: str, params: dict) -> dict:
    """
    根据参数别名表自动映射参数名。
    """
    aliases = PARAM_ALIASES.get(tool_name, {})
    return {aliases.get(k, k): v for k, v in params.items()}
