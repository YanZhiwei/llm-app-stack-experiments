# ReAct 推理智能体系统

基于 LangGraph 的标准 ReAct(Reasoning and Acting) 推理智能体系统，专注于**推理过程**和**工具调用**的核心功能。

## 🌟 核心特性

### 🧠 标准 ReAct 推理

- **Thought → Action → Observation → Thought** 循环模式
- **自动工具选择**：通过 `llm.bind_tools()` 实现智能工具调用
- **推理链追踪**：完整的推理过程记录
- **最终答案提取**：自动识别和提取最终答案

### 🔧 精简工具集

- **6 个核心工具**：搜索、计算、时间处理
- **模块化设计**：易于扩展和维护
- **标准接口**：使用 `@tool` 装饰器

### 🎯 工具详情

#### 📂 核心工具 (6 个)

- `search_information` - 搜索信息（知识库查询）
- `calculate_math` - 数学计算（支持数学函数）
- `get_current_time` - 获取当前时间
- `calculate_date_difference` - 计算日期差异
- `get_calendar_info` - 获取日历信息
- `add_days_to_date` - 日期计算

## 🚀 快速开始

### 1. 环境设置

```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install .

# 生成锁定文件
uv lock
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# Azure OpenAI 配置
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. 运行程序

```bash
# 交互模式
python main.py

# 命令行参数模式
python main.py "计算圆的面积，半径是5米"
```

## 🎯 示例问题

项目内置了 5 个优秀的 ReAct 示例问题：

### 1. 🌟 基础 ReAct 推理 - 数学计算

```bash
python main.py "计算圆的面积，半径是5米，然后告诉我这个面积相当于多少个边长为2米的正方形"
```

### 2. 📅 时间推理 - 日期计算

```bash
python main.py "今天是几号？如果我要在30天后举办一个活动，那天是星期几？距离春节还有多少天？"
```

### 3. 🎯 综合推理 - 多工具组合（推荐）

```bash
python main.py "帮我规划一个周末活动：查询明天天气，如果天气好就推荐户外活动，如果不好就推荐室内活动，并计算大概需要多少时间"
```

### 4. 📚 复杂推理 - 问题分解

```bash
python main.py "我需要学习Python编程，帮我制定一个学习计划：查询Python的基础知识，计算学习时间，并告诉我每天应该学习多长时间"
```

### 5. 🤖 高级推理 - 多步骤问题

```bash
python main.py "我想了解人工智能的发展趋势，查询相关信息，分析当前的技术水平，并预测未来5年的发展方向"
```

## 🔧 技术架构

### 核心组件

- **`main.py`** - 主程序入口，支持命令行参数和交互输入
- **`agents.py`** - ReAct 推理智能体，使用 `llm.bind_tools()` 实现工具调用
- **`orchestrator.py`** - LangGraph 工作流编排器
- **`prompts.py`** - ReAct 提示词管理
- **`state.py`** - 状态定义 (ReActState)
- **`config.py`** - 配置管理

### 工具系统

```
tools/
├── __init__.py          # 工具导入和分类
├── calculator_tool.py    # 数学计算工具
├── datetime_tool.py     # 日期时间工具
└── search_tool.py       # 搜索工具
```

### 技术栈

- **Python 3.12+**
- **LangChain & LangGraph**
- **Azure OpenAI**
- **Requests**
- **Python-dotenv**

## 📁 项目结构

```
react-reasoning-agent/
├── main.py                    # 主程序入口
├── agents.py                  # ReAct推理智能体
├── orchestrator.py            # 工作流编排器
├── prompts.py                 # 提示词管理
├── state.py                   # 状态定义
├── config.py                  # 配置管理
├── tools/                     # 工具库
│   ├── __init__.py           # 工具导入和分类
│   ├── calculator_tool.py    # 数学计算工具
│   ├── datetime_tool.py      # 日期时间工具
│   └── search_tool.py        # 搜索工具
├── pyproject.toml            # 项目配置
├── uv.lock                   # 依赖锁定文件
└── README.md                 # 项目文档
```

## 🧠 ReAct 推理流程

### 标准 ReAct 模式

```
用户问题 → Thought → Action → Observation → Thought → ... → Final Answer
```

### 工作流组件

1. **Reasoning Agent** - 推理智能体

   - 分析问题
   - 选择工具
   - 生成推理链

2. **Tool Node** - 工具执行节点

   - 执行工具调用
   - 返回观察结果

3. **Executor Agent** - 执行智能体
   - 处理工具结果
   - 决定下一步行动

## 🎯 适用场景

- 🤖 **AI 助手开发**：作为标准 ReAct 推理系统的基础框架
- 🔧 **工具集成平台**：快速集成和测试新工具
- 📚 **教学演示**：展示 ReAct 推理方法和 LangGraph 应用
- 🧪 **原型开发**：快速构建推理系统原型
- 📊 **问题分解**：将复杂问题分解为可执行的步骤

## 🔮 未来规划

- [ ] 增加更多专业工具（代码生成、数据可视化等）
- [ ] 支持多模态输入（图像、语音）
- [ ] 优化推理性能和准确度
- [ ] 添加 Web 界面和 API 接口
- [ ] 支持自定义工具插件
- [ ] 增加协作推理功能

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献方式

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发送 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 添加适当的测试
- 更新相关文档

---

**体验标准 ReAct 推理系统的强大功能！** 🎉
