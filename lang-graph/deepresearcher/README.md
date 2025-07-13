# Research Agent

基于 Google Gemini Fullstack LangGraph 项目架构的简化研究代理。

## 项目结构

```
deepresearcher/
├── agent.py          # 主要的agent逻辑
├── config.py         # 配置管理
├── graph.py          # 图构建
├── main.py           # 主程序入口
├── nodes.py          # 节点函数
├── state.py          # 状态定义
├── env_example.env   # 环境变量示例
├── pyproject.toml    # 项目配置
└── README.md         # 项目说明
```

## 功能特性

- 🔍 **智能查询生成**: 基于研究主题自动生成多个搜索查询
- 🌐 **多源搜索**: 支持 Tavily 和 DuckDuckGo 搜索引擎
- 🤖 **AI 分析**: 使用 Azure OpenAI 进行内容分析和答案生成
- 📊 **结构化输出**: 生成包含概述、发现、要点和结论的完整报告
- 🔄 **流式处理**: 支持流式运行，实时显示进度

## 安装

1. 克隆项目

```bash
git clone <repository-url>
cd deepresearcher
```

2. 安装依赖

```bash
uv venv
uv pip install -r requirements.txt
```

3. 配置环境变量

```bash
cp env_example.env .env
# 编辑.env文件，填入您的API密钥
```

## 环境变量配置

在`.env`文件中配置以下变量：

```env
# Azure OpenAI配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your_deployment_name

# 搜索引擎配置（可选）
TAVILY_API_KEY=your_tavily_api_key
```

## 使用方法

### 命令行运行

```bash
python main.py
```

程序会提示您选择研究主题或输入自定义问题。

### 编程接口

```python
from agent import run_research

# 运行研究
result = run_research("人工智能在医疗诊断中的应用")
print(result['answer'])
```

### 流式运行

```python
from agent import stream_research

# 流式运行研究
for state in stream_research("量子计算的发展"):
    print(state)
```

## 工作流程

1. **查询生成**: 基于研究主题生成 3 个不同的搜索查询
2. **网络搜索**: 使用配置的搜索引擎执行搜索
3. **内容分析**: 使用 AI 分析搜索结果并生成结构化答案
4. **结果输出**: 返回包含概述、发现、要点和结论的完整报告

## 技术栈

- **LangGraph**: 工作流编排
- **Azure OpenAI**: AI 模型服务
- **Tavily**: 高级搜索引擎
- **DuckDuckGo**: 备用搜索引擎
- **Pydantic**: 数据验证和序列化

## 开发

### 项目结构说明

- `state.py`: 定义 Agent 状态结构
- `config.py`: 管理配置和 API 密钥
- `nodes.py`: 包含所有节点函数（查询生成、搜索、答案生成）
- `graph.py`: 构建 LangGraph 工作流
- `agent.py`: 主要的 agent 接口
- `main.py`: 命令行界面

### 添加新节点

1. 在`nodes.py`中定义新的节点函数
2. 在`graph.py`中添加节点到工作流
3. 更新状态定义（如需要）

### 自定义搜索引擎

在`nodes.py`的`search_web`函数中添加新的搜索引擎支持。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
