# ReAct推理智能体系统

## 项目简介

ReAct推理智能体是基于 [LangGraph](https://github.com/langchain-ai/langgraph) 和 [LangChain](https://github.com/langchain-ai/langchain) 的智能推理系统，实现了 **ReAct (Reasoning and Acting)** 推理方法。

ReAct是一种让大模型通过 **思考(Think) → 行动(Act) → 观察(Observe)** 的循环来解决复杂问题的推理框架。

## 🧠 ReAct方法介绍

**ReAct** = **Reasoning** (推理) + **Acting** (行动)

### 核心思想
- **交替推理与行动**: 不是一次性生成答案，而是逐步推理
- **工具辅助**: 通过调用外部工具获取信息
- **可解释性**: 完整的思考过程透明可见
- **迭代优化**: 基于观察结果调整后续策略

### 工作流程
```
问题输入 → 分析思考 → 选择工具 → 执行行动 → 观察结果 → 继续推理或得出答案
```

## 🚀 主要功能

- **智能问题分析**: 自动识别问题类型并制定解决策略
- **多样化工具集**: 搜索、计算、记忆、验证等工具
- **推理链追踪**: 完整记录思考过程和决策路径
- **自适应推理**: 根据中间结果动态调整策略
- **答案验证**: 自动评估答案质量和合理性

## 🛠️ 可用工具

| 工具名称 | 功能描述 | 使用场景 |
|---------|---------|----------|
| `search_information` | 搜索相关信息 | 知识查询、概念解释 |
| `calculate_math` | 数学计算 | 数值计算、公式求解 |
| `analyze_problem` | 问题分析 | 策略制定、类型识别 |
| `store_memory` | 存储信息 | 保存重要发现 |
| `retrieve_memory` | 检索信息 | 回顾历史信息 |
| `verify_answer` | 验证答案 | 质量检查、合理性评估 |

## 📋 依赖环境

- Python 3.12+
- [LangChain](https://pypi.org/project/langchain/) >= 0.3.26
- [LangGraph](https://pypi.org/project/langgraph/) >= 0.5.2
- [LangChain-OpenAI](https://pypi.org/project/langchain-openai/) >= 0.1.0
- 推荐使用 [uv](https://github.com/astral-sh/uv) 进行环境管理

## 🔧 安装与运行

### 1. 环境准备

```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install .

# 生成依赖锁定文件
uv lock
```

### 2. 配置环境变量（可选）

如果需要使用Azure OpenAI进行智能推理，创建 `.env` 文件：

```bash
# Azure OpenAI配置
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. 运行示例

```bash
python main.py
```

## 📁 项目结构

```
react-intro/
├── main.py              # 程序入口
├── orchestrator.py      # 工作流编排器
├── agents.py           # ReAct推理智能体
├── state.py            # 状态管理
├── tools/              # 工具集
│   ├── __init__.py
│   ├── search_tool.py      # 信息搜索工具
│   ├── calculator_tool.py  # 数学计算工具
│   ├── reasoning_tool.py   # 问题分析工具
│   ├── memory_tool.py      # 记忆管理工具
│   └── verification_tool.py # 答案验证工具
├── pyproject.toml      # 项目配置
└── README.md          # 项目说明
```

## 🎯 使用示例

### 数学计算问题
```
问题: 计算 (5 + 3) * 2 - 1 的结果

推理过程:
1. 思考: 这是一个数学计算问题，需要按照运算优先级计算
2. 行动: 使用calculate_math工具
3. 观察: 计算结果为15
4. 结论: 答案是15
```

### 知识查询问题
```
问题: 什么是LangGraph？

推理过程:
1. 思考: 这是一个概念查询问题，需要搜索相关信息
2. 行动: 使用search_information工具
3. 观察: 找到LangGraph的定义和特点
4. 结论: LangGraph是用于构建多智能体应用的框架...
```

### 复杂推理问题
```
问题: 比较Python和Java的优缺点

推理过程:
1. 思考: 需要分别获取两种语言的信息进行比较
2. 行动: 搜索Python特点
3. 观察: 获得Python信息
4. 思考: 还需要Java的信息
5. 行动: 搜索Java特点
6. 观察: 获得Java信息
7. 结论: 综合比较两种语言的优缺点...
```

## 🧪 自定义配置

### 修改最大推理轮次
在 `main.py` 中修改：
```python
initial_state: ReActState = {
    # ...
    "max_iterations": 3,  # 默认为5
    # ...
}
```

### 添加自定义工具
1. 在 `tools/` 目录创建新工具文件
2. 使用 `@tool` 装饰器定义工具函数
3. 在 `tools/__init__.py` 中注册新工具

### 修改问题类型检测
在 `tools/reasoning_tool.py` 中的 `problem_types` 字典添加新的问题类型和关键词。

## 🔍 核心组件说明

### ReActState (状态管理)
定义了推理过程中的所有状态信息：
- `reasoning_chain`: 完整的推理链记录
- `current_iteration`: 当前推理轮次
- `thought_process`: 思考过程记录
- `final_answer`: 最终答案

### 智能体 (Agents)
- **`react_reasoning_agent`**: 负责分析问题、制定策略、选择工具
- **`react_executor_agent`**: 处理工具执行结果、决定下一步行动

### 工作流编排 (Orchestrator)
定义了 reasoning → tools → executor 的循环流程，支持条件跳转和迭代控制。

## 🎨 扩展建议

1. **增加更多工具**: 如文件操作、网络请求、数据库查询等
2. **优化推理策略**: 根据问题类型采用不同的推理模式
3. **添加并行推理**: 支持同时探索多个解决路径
4. **集成外部知识库**: 连接真实的搜索引擎或知识图谱
5. **可视化推理过程**: 生成推理链的图形化展示

## 📚 参考资料

- [ReAct论文](https://arxiv.org/abs/2210.03629): Synergizing Reasoning and Acting in Language Models
- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain官方文档](https://python.langchain.com/)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个ReAct推理系统！

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。 