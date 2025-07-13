# ReAct 推理系统 - 智能升级版

基于 LangGraph 的 ReAct(Reasoning and Acting)推理智能体系统，现已升级到 **49 个实用工具**，支持**智能推理策略选择**和**结果质量评估**！

## 🌟 核心特性

### 🧠 智能推理系统

- **多种推理策略**：顺序、并行、层次、自适应、聚焦、探索推理
- **复杂度分析**：自动分析问题复杂度并选择合适策略
- **智能迭代控制**：根据任务复杂度自动调整迭代次数
- **结果质量评估**：自动评估推理结果质量并提供优化建议

### 🔧 工具数量升级

- **原版**: 30+个基础工具
- **升级版**: **49 个专业工具**，覆盖 **9 大类别**

### 🎯 工具分类详情

#### 📂 核心工具 (7 个)

- `search_information` - 搜索信息
- `calculate_math` - 数学计算（支持数学函数）
- `analyze_problem` - 问题分析
- `store_memory` - 存储记忆
- `retrieve_memory` - 检索记忆
- `verify_answer` - 验证答案
- `generate_detailed_content` - 基于源材料生成详细结构化内容

#### 📂 日期时间工具 (4 个)

- `get_current_time` - 获取当前时间
- `calculate_date_difference` - 计算日期差异
- `get_calendar_info` - 获取日历信息
- `add_days_to_date` - 日期计算

#### 📂 文本处理工具 (4 个)

- `analyze_text` - 文本分析（统计、词频、可读性）
- `format_text` - 文本格式化（大小写、命名规范）
- `extract_patterns` - 模式提取（邮箱、URL、电话等）
- `text_similarity` - 文本相似度计算

#### 📂 Markdown 工具 (6 个)

- `create_markdown_report` - 创建 Markdown 报告
- `create_markdown_table` - 创建 Markdown 表格
- `format_markdown_content` - 格式化 Markdown 内容
- `create_business_trip_report` - 创建专业商务出差报告
- `create_enhanced_markdown_table` - 创建增强版 Markdown 表格
- `create_text_chart` - 创建文本图表（ASCII 风格）

#### 📂 单位转换工具 (6 个)

- `convert_length` - 长度转换
- `convert_weight` - 重量转换
- `convert_temperature` - 温度转换
- `convert_area` - 面积转换
- `convert_volume` - 体积转换
- `convert_speed` - 速度转换

#### 📂 在线 API 工具 (8 个)

- `get_weather_info` - 天气信息 (wttr.in)
- `get_exchange_rate` - 汇率信息 (exchangerate-api.com)
- `get_ip_location` - IP 地理位置 (ipapi.co)
- `generate_qr_code` - 二维码生成 (qr-server.com)
- `get_random_joke` - 随机笑话 (official-joke-api)
- `get_random_quote` - 随机名言 (quotable.io)
- `shorten_url` - 短链接生成 (tinyurl.com)
- `get_random_image_url` - 随机图片 (picsum.photos)

#### 📂 航班工具 (3 个)

- `search_flights` - 航班查询（支持模拟和真实 API）
- `get_airport_info` - 机场信息查询
- `get_flight_price_alert` - 航班价格提醒

#### 📂 随机生成工具 (6 个)

- `generate_password` - 密码生成（强度分析）
- `generate_random_numbers` - 随机数生成
- `generate_uuid` - UUID 生成
- `generate_random_text` - 随机文本生成
- `generate_random_choice` - 随机选择
- `generate_random_date` - 随机日期生成

#### 📂 日志分析工具 (5 个)

- `get_reasoning_summary` - 推理过程摘要
- `get_tool_performance_report` - 工具性能报告
- `get_current_session_info` - 当前会话信息
- `export_logs_json` - 导出日志 JSON
- `clear_logs` - 清除日志记录

## 🚀 环境设置

### 1. 基础环境

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
# 运行主程序（使用默认演示问题）
python main.py
```

### 4. 演示问题集合

项目内置了 10 个演示问题，展示不同功能模块：

1. **🌤️ 天气查询 + 文本分析** (默认启用)
2. **🧮 数学计算 + 单位转换**
3. **📅 日期时间 + 日历分析**
4. **✈️ 航班查询 + 机场信息**
5. **🎲 随机生成 + 密码安全**
6. **📝 Markdown 报告 + 图表生成**
7. **🔍 文本处理 + 模式提取**
8. **🌐 综合查询 + 汇率转换**
9. **🧠 复杂推理 + 内容生成**
10. **📊 数据分析 + 日志统计**

**切换演示问题**：

- 打开 `main.py` 文件
- 在第 17-65 行找到演示问题集合
- 注释掉当前问题，取消注释想要演示的问题
- 重新运行程序

## 🎯 推理策略

### 策略类型

- **顺序推理** (sequential) - 逐步推理，适合复杂问题
- **并行推理** (parallel) - 并行处理，提高效率
- **层次推理** (hierarchical) - 分层分析，处理复杂结构
- **自适应推理** (adaptive) - 动态调整，最灵活
- **聚焦推理** (focused) - 专注特定领域
- **探索推理** (exploratory) - 广泛探索，发现新思路

### 智能调整

- **复杂度分析**：自动评估问题复杂度
- **策略选择**：根据复杂度自动选择最佳策略
- **迭代控制**：智能调整迭代次数（6-40 轮）
- **质量评估**：自动评估结果质量并提供建议

## 📝 示例问题

### 基础功能

```python
# 数学计算
"请计算 sin(π/4) + cos(π/3) 的值"

# 日期时间
"今天是几月几号？显示2024年12月的日历"

# 文本处理
"分析这段文本的详细信息：'人工智能正在改变世界'"
```

### 专业功能

```python
# 航班查询
"查询明天从上海到北京的航班信息"

# Markdown报告
"创建一个关于AI发展的专业报告"

# 随机生成
"生成一个16位的强密码，包含特殊字符"
```

### 综合任务

```python
# 项目规划
"我需要规划一个AI项目，帮我分析步骤并生成Markdown报告"

# 数据分析
"分析用户反馈数据，计算满意度并生成图表"
```

## 🔧 技术架构

### 核心组件

- **智能体系统**：基于 LangGraph 的 ReAct 推理
- **工具管理**：模块化工具设计，支持动态加载
- **推理策略**：多种推理模式，自适应选择
- **质量评估**：结果质量自动评估

### 配置系统

- **迭代控制**：严格/智能/灵活三种模式
- **动态调整**：根据任务复杂度自动扩展
- **安全限制**：最大迭代次数保护

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
├── state.py                   # 状态定义
├── config.py                  # 配置管理
├── reasoning_strategies.py    # 推理策略管理
├── tools/                     # 工具库
│   ├── __init__.py                  # 工具导入和分类
│   ├── calculator_tool.py           # 数学计算工具
│   ├── search_tool.py               # 搜索工具
│   ├── reasoning_tool.py            # 推理工具
│   ├── memory_tool.py               # 记忆工具
│   ├── verification_tool.py         # 验证工具
│   ├── datetime_tool.py             # 日期时间工具
│   ├── text_processing_tool.py      # 文本处理工具
│   ├── markdown_tool.py             # Markdown工具
│   ├── unit_converter_tool.py       # 单位转换工具
│   ├── online_api_tool.py           # 在线API工具
│   ├── flight_tool.py               # 航班工具
│   ├── random_generator_tool.py     # 随机生成工具
│   ├── logging_tool.py              # 日志工具
│   ├── mcp_adapter.py               # MCP适配器
│   ├── tool_resolver.py             # 工具解析器
│   └── ...
├── pyproject.toml             # 项目配置
├── uv.lock                    # 依赖锁定文件
└── README.md                  # 项目文档
```

## 🌐 免费 API 服务

| 服务                 | API             | 功能             |
| -------------------- | --------------- | ---------------- |
| wttr.in              | 天气 API        | 获取全球天气信息 |
| exchangerate-api.com | 汇率 API        | 实时汇率查询     |
| ipapi.co             | IP 地理位置 API | IP 地址定位      |
| qr-server.com        | 二维码 API      | 生成二维码       |
| official-joke-api    | 笑话 API        | 随机英文笑话     |
| quotable.io          | 名言 API        | 随机名言         |
| tinyurl.com          | 短链接 API      | URL 缩短         |
| picsum.photos        | 图片 API        | 随机图片         |

## 📊 性能统计

- 🔧 **工具数量**: 49 个
- 📂 **工具分类**: 9 大类
- 🌐 **免费 API**: 8 个服务
- 🧠 **推理策略**: 6 种策略
- 📝 **代码行数**: 6000+ 行
- 🎯 **支持语言**: 中文 + 英文
- 📊 **功能模块**: 推理、工具、日志、配置

## 🎯 适用场景

- 🤖 **AI 助手开发**：作为多功能 AI 助手的基础框架
- 🔧 **工具集成平台**：快速集成各种实用工具
- 📚 **教学演示**：展示 ReAct 推理方法和 LangGraph 应用
- 🧪 **原型开发**：快速构建推理系统原型
- 📊 **数据分析**：集成多种数据处理和分析工具
- 📝 **文档生成**：自动生成专业 Markdown 文档

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

**体验 ReAct 推理系统的强大功能！** 🎉
