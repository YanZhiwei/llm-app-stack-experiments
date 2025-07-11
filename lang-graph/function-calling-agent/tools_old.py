import json
import math
import os
from datetime import datetime

import requests
from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """使用 DuckDuckGo 进行免费联网搜索"""
    try:
        # 使用 DuckDuckGo 搜索
        with DDGS() as ddgs:
            # 获取前5个搜索结果
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            return f"没有找到关于 '{query}' 的搜索结果"
        
        # 格式化搜索结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', '无标题')
            body = result.get('body', '无描述')
            href = result.get('href', '无链接')
            
            formatted_results.append(
                f"{i}. {title}\n"
                f"   描述: {body[:200]}{'...' if len(body) > 200 else ''}\n"
                f"   链接: {href}\n"
            )
        
        return f"搜索关键词: {query}\n\n" + "\n".join(formatted_results)
        
    except Exception as e:
        return f"搜索失败: {str(e)}。请检查网络连接或稍后重试。"


@tool
def calculate(expression: str) -> str:
    """执行数学计算，支持基本运算和数学函数"""
    try:
        # 安全的数学表达式计算
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}。请检查表达式格式，例如: 2+3*4, sqrt(16), sin(pi/2)"


@tool
def get_current_time() -> str:
    """获取当前时间和日期"""
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S %A')}"


@tool
def write_file(filename: str, content: str) -> str:
    """将内容写入文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功将内容写入文件: {filename}"
    except Exception as e:
        return f"写入文件失败: {str(e)}"


@tool
def read_file(filename: str) -> str:
    """读取文件内容"""
    try:
        if not os.path.exists(filename):
            return f"文件不存在: {filename}"
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果文件太大，只返回前1000个字符
        if len(content) > 1000:
            return f"文件内容 (前1000字符): {content[:1000]}...\n\n文件总长度: {len(content)} 字符"
        else:
            return f"文件内容: {content}"
    except Exception as e:
        return f"读取文件失败: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """列出指定目录下的文件和文件夹"""
    try:
        if not os.path.exists(directory):
            return f"目录不存在: {directory}"
        
        items = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                items.append(f"📄 {item} ({size} bytes)")
        
        return f"目录 '{directory}' 的内容:\n" + "\n".join(items)
    except Exception as e:
        return f"列出文件失败: {str(e)}"


@tool
def translate_text(text: str, target_language: str = "en") -> str:
    """使用免费翻译服务翻译文本"""
    try:
        # 使用 DuckDuckGo 的翻译功能
        with DDGS() as ddgs:
            result = ddgs.translate(text, to=target_language)
            if result:
                return f"翻译结果 ({target_language}): {result}"
            else:
                return "翻译失败，请检查输入文本和目标语言代码"
    except Exception as e:
        return f"翻译失败: {str(e)}。支持的语言代码如: en(英语), zh(中文), ja(日语), ko(韩语), fr(法语), de(德语), es(西班牙语)"


@tool
def analyze_data(data: str) -> str:
    """分析数据并提供统计信息"""
    try:
        # 尝试解析为JSON数组
        if data.startswith('[') and data.endswith(']'):
            numbers = json.loads(data)
            if all(isinstance(x, (int, float)) for x in numbers):
                avg = sum(numbers) / len(numbers)
                return f"数据分析结果:\n数量: {len(numbers)}\n平均值: {avg:.2f}\n最大值: {max(numbers)}\n最小值: {min(numbers)}\n总和: {sum(numbers)}"
        
        # 尝试解析为逗号分隔的数字
        if ',' in data:
            numbers = [float(x.strip()) for x in data.split(',')]
            avg = sum(numbers) / len(numbers)
            return f"数据分析结果:\n数量: {len(numbers)}\n平均值: {avg:.2f}\n最大值: {max(numbers)}\n最小值: {min(numbers)}\n总和: {sum(numbers)}"
        
        # 文本分析
        words = data.split()
        return f"文本分析结果:\n字符数: {len(data)}\n单词数: {len(words)}\n行数: {len(data.splitlines())}"
        
    except Exception as e:
        return f"数据分析失败: {str(e)}。支持格式: [1,2,3,4] 或 1,2,3,4 或普通文本"


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息（使用搜索获取）"""
    try:
        # 使用搜索获取天气信息
        query = f"{city} 天气 今天"
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if results:
            weather_info = []
            for result in results:
                if '天气' in result.get('title', '') or '气温' in result.get('body', ''):
                    weather_info.append(f"• {result.get('title', '')}\n  {result.get('body', '')[:150]}...")
            
            if weather_info:
                return f"{city} 天气信息:\n\n" + "\n\n".join(weather_info)
            else:
                return f"未找到 {city} 的详细天气信息，建议使用更具体的城市名称"
        else:
            return f"无法获取 {city} 的天气信息"
    except Exception as e:
        return f"获取天气信息失败: {str(e)}"


def get_tools():
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