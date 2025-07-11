# 工具包 (Tools Package)

这个文件夹包含了 Super Agent 系统的所有工具。每个工具都被组织在单独的文件中，便于维护和扩展。

## 工具列表

### 🔍 网络搜索 (`web_search.py`)
- **功能**: 使用 DuckDuckGo 进行免费联网搜索
- **参数**: `query` (搜索关键词)
- **示例**: 搜索 "LangGraph 教程"

### 🧮 计算器 (`calculator.py`)
- **功能**: 执行数学计算，支持基本运算和数学函数
- **参数**: `expression` (数学表达式)
- **示例**: `2+3*4`, `sqrt(16)`, `sin(pi/2)`

### ⏰ 时间工具 (`time_tool.py`)
- **功能**: 获取当前时间和日期
- **参数**: 无
- **返回**: 格式化的当前时间

### 📁 文件工具 (`file_tools.py`)
包含三个文件操作工具：
- **write_file**: 写入文件内容
- **read_file**: 读取文件内容
- **list_files**: 列出目录内容

### 🌐 翻译工具 (`translator.py`)
- **功能**: 使用免费翻译服务翻译文本
- **参数**: `text` (待翻译文本), `target_language` (目标语言代码)
- **支持语言**: en, zh, ja, ko, fr, de, es 等

### 📊 数据分析 (`data_analyzer.py`)
- **功能**: 分析数据并提供统计信息
- **参数**: `data` (数据，支持JSON数组、逗号分隔数字或文本)
- **返回**: 统计信息（平均值、最大值、最小值等）

### 🌤️ 天气查询 (`weather.py`)
- **功能**: 获取指定城市的天气信息
- **参数**: `city` (城市名称)
- **示例**: 查询 "北京" 的天气

## 如何添加新工具

1. 在 `tools/` 文件夹中创建新的 `.py` 文件
2. 使用 `@tool` 装饰器定义工具函数
3. 在 `__init__.py` 中导入新工具
4. 将新工具添加到 `get_tools()` 函数的返回列表中
5. 更新 `__all__` 列表

### 示例新工具模板：

```python
"""
新工具 - 工具描述
"""

from langchain_core.tools import tool

@tool
def my_new_tool(param1: str, param2: int = 0) -> str:
    """工具功能描述"""
    try:
        # 工具逻辑
        result = f"处理结果: {param1} + {param2}"
        return result
    except Exception as e:
        return f"工具执行失败: {str(e)}"
```

## 工具规范

1. **错误处理**: 每个工具都应该有适当的异常处理
2. **类型注解**: 使用类型注解明确参数和返回值类型
3. **文档字符串**: 提供清晰的功能描述
4. **返回格式**: 返回用户友好的字符串格式结果
5. **模块化**: 每个工具应该是独立的，不依赖其他工具 