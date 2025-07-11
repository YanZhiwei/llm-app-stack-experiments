"""
工具包 - 包含所有可用的工具
"""

from .calculator import calculate
from .data_analyzer import analyze_data
from .file_tools import list_files, read_file, write_file
from .time_tool import get_current_time
from .translator import translate_text
from .weather import get_weather
from .web_search import web_search


def get_tools():
    """获取所有可用工具的列表"""
    return [
        web_search,
        calculate, 
        get_current_time,
        write_file,
        read_file,
        list_files,
        translate_text,
        analyze_data,
        get_weather
    ]


__all__ = [
    'get_tools',
    'web_search',
    'calculate',
    'get_current_time',
    'write_file',
    'read_file',
    'list_files',
    'translate_text',
    'analyze_data',
    'get_weather'
] 