import os
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage

# 新增导入
from langchain_openai import AzureChatOpenAI

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续执行
    pass

if TYPE_CHECKING:
    from state import SuperAgentState

# Azure OpenAI 配置（可通过环境变量设置）
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

llm = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        openai_api_key=AZURE_OPENAI_API_KEY,
        temperature=0.2,
    )

async def planner_agent(state: 'SuperAgentState') -> 'SuperAgentState':
    """规划Agent：使用 LLM 智能选择合适的工具"""
    
    # 获取用户的原始消息
    user_message = ""
    for msg in state["messages"]:
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            user_message = msg.content
            break
    
    # 如果配置了Azure OpenAI，使用 LLM 进行智能工具选择
    if llm:
        try:
            # 构建工具描述，让 LLM 了解可用工具
            tools_description = """
可用工具列表：
1. web_search(query: str) - 网络搜索，用于查找信息、了解概念、获取最新资讯
2. calculate(expression: str) - 数学计算，支持基本运算和数学函数
3. get_current_time() - 获取当前时间和日期
4. write_file(filename: str, content: str) - 写入文件
5. read_file(filename: str) - 读取文件内容
6. list_files(directory: str) - 列出目录内容
7. translate_text(text: str, target_language: str) - 翻译文本
8. analyze_data(data: str) - 数据分析和统计
9. get_weather(city: str) - 查询城市天气信息
"""

            prompt = f"""你是一个智能助手规划器。用户请求："{user_message}"

{tools_description}

请分析用户的请求，选择最合适的工具并确定参数。

请按以下JSON格式回复：
{{
    "selected_tool": "工具名称",
    "tool_args": {{"参数名": "参数值"}},
    "reasoning": "选择这个工具的原因"
}}

只返回JSON，不要其他内容。"""

            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            # 尝试解析 LLM 的响应
            import json
            try:
                # 提取JSON部分
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                tool_decision = json.loads(content.strip())
                selected_tool = tool_decision.get("selected_tool")
                tool_args = tool_decision.get("tool_args", {})
                reasoning = tool_decision.get("reasoning", "LLM 智能选择")
                
                # 验证工具名称是否有效
                valid_tools = [
                    "web_search", "calculate", "get_current_time", "write_file", 
                    "read_file", "list_files", "translate_text", "analyze_data", "get_weather"
                ]
                
                if selected_tool not in valid_tools:
                    # 如果工具名称无效，回退到默认搜索
                    selected_tool = "web_search"
                    tool_args = {"query": user_message}
                    reasoning = "工具名称无效，回退到搜索"
                
            except (json.JSONDecodeError, KeyError) as e:
                # JSON解析失败，回退到默认搜索
                selected_tool = "web_search"
                tool_args = {"query": user_message}
                reasoning = f"LLM响应解析失败: {e}，回退到搜索"
            
            # 创建工具调用
            tool_call = {
                "name": selected_tool,
                "args": tool_args,
                "id": "call_llm_smart"
            }
            
            ai_message = AIMessage(
                content=f"我分析了您的请求，决定使用 {selected_tool} 工具。\n\n推理过程: {reasoning}",
                tool_calls=[tool_call]
            )
            
            return {
                **state,
                "messages": state["messages"] + [ai_message],
                "reasoning_log": state["reasoning_log"] + [
                    "规划完成（LLM智能选择）", 
                    f"选择工具: {selected_tool}", 
                    f"工具参数: {tool_args}",
                    f"推理过程: {reasoning}"
                ],
                "next_action": "execute_tools"
            }
            
        except Exception as e:
            # LLM 调用失败时，使用简化的启发式规则
            pass
    
    # 回退方案：使用改进的启发式规则（比原来更智能）
    task_lower = (state['current_task'] + " " + user_message).lower()
    
    # 使用更智能的匹配逻辑
    if any(word in task_lower for word in ['天气', 'weather', '气温', '温度', '下雨', '晴天', '阴天']):
        selected_tool = "get_weather"
        # 智能提取城市名
        import re
        cities = re.findall(r'[北京上海广州深圳杭州南京成都重庆天津武汉西安]', task_lower)
        city = cities[0] if cities else "北京"
        tool_args = {"city": city}
        reasoning = f"检测到天气查询，提取城市: {city}"
        
    elif any(word in task_lower for word in ['计算', '算', '数学', 'calculate']) or any(op in task_lower for op in ['+', '-', '*', '/', '=', '平方', '开方']):
        selected_tool = "calculate"
        # 智能提取数学表达式
        import re
        math_expr = re.search(r'[\d+\-*/().\s]+', user_message)
        expression = math_expr.group().strip() if math_expr else "2+2"
        tool_args = {"expression": expression}
        reasoning = f"检测到数学计算，表达式: {expression}"
        
    elif any(word in task_lower for word in ['时间', 'time', '现在', '几点', '日期', '今天']):
        selected_tool = "get_current_time"
        tool_args = {}
        reasoning = "检测到时间查询"
        
    elif any(word in task_lower for word in ['翻译', 'translate', '英文', '中文', '日文', '法文']):
        selected_tool = "translate_text"
        # 智能检测目标语言
        target_lang = "en"
        if any(word in task_lower for word in ['中文', '汉语', '中国话']):
            target_lang = "zh"
        elif any(word in task_lower for word in ['日文', '日语', '日本话']):
            target_lang = "ja"
        tool_args = {"text": user_message, "target_language": target_lang}
        reasoning = f"检测到翻译请求，目标语言: {target_lang}"
        
    else:
        # 默认使用搜索
        selected_tool = "web_search"
        tool_args = {"query": user_message}
        reasoning = "未匹配到特定工具，使用搜索"
    
    # 创建工具调用
    tool_call = {
        "name": selected_tool,
        "args": tool_args,
        "id": "call_heuristic"
    }
    
    ai_message = AIMessage(
        content=f"我分析了您的请求，决定使用 {selected_tool} 工具。\n\n推理过程: {reasoning}",
        tool_calls=[tool_call]
    )
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "reasoning_log": state["reasoning_log"] + [
            "规划完成（启发式规则）", 
            f"选择工具: {selected_tool}", 
            f"工具参数: {tool_args}",
            f"推理过程: {reasoning}"
        ],
        "next_action": "execute_tools"
    }

async def executor_agent(state: 'SuperAgentState') -> 'SuperAgentState':
    """执行Agent"""
    # The executor should process the tool results from the state.
    # The ToolNode will add one or more ToolMessages to the state.
    last_message = state["messages"][-1]
    tool_output = last_message.content
    return {
        **state,
        "final_result": f"任务完成，工具输出: {tool_output}",
        "reasoning_log": state["reasoning_log"] + ["执行完成", f"处理工具输出: {tool_output}"]
    }