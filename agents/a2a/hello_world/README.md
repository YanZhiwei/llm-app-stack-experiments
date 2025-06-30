# Hello World A2A Agent

这是一个基于 Google A2A (Agent-to-Agent) Python SDK 的简单入门示例，演示如何创建一个基础的 A2A 代理服务。

## 功能特性

- 🤖 **简单问候**: 提供基本的问候功能
- 💬 **消息回显**: 可以回显和处理用户消息
- 🔄 **流式响应**: 支持流式消息返回
- 🛠️ **帮助系统**: 内置帮助功能
- 🌐 **HTTP 服务**: 提供 REST API 接口

## 目录结构

```
hello_world/
├── __init__.py
├── main.py           # 程序入口（命令行/服务启动）
├── core_agent.py     # 代理核心逻辑 HelloWorldAgent
├── executor.py       # 代理执行器 HelloWorldAgentExecutor
├── card.py           # AgentCard/AgentSkill 定义
├── client.py         # 本地测试客户端
├── pyproject.toml
├── README.md
└── uv.lock
```

## 快速开始

### 前置要求

- Python 3.10+
- uv (推荐) 或 pip

### 安装依赖

```bash
uv sync
```

### 启动代理服务

```bash
python main.py
# 或
uv run main.py
# 或指定端口
python main.py --host 0.0.0.0 --port 8080
```

### 使用客户端测试

1. 启动服务后，运行本地测试客户端：

```bash
python client.py "hello"
python client.py "help"
python client.py "test echo"
```

2. 也可直接用 curl 测试：

```bash
curl -X POST http://localhost:9999/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"kind": "text", "text": "hello"}]}}'
```

## 代码说明

- `main.py`：命令行入口，负责服务启动和参数解析。
- `core_agent.py`：HelloWorldAgent 逻辑。
- `executor.py`：A2A AgentExecutor 实现。
- `card.py`：AgentCard/AgentSkill 定义与创建。
- `client.py`：本地测试客户端，便于开发调试。

## 扩展建议

- 可在 core_agent.py 中扩展更多智能逻辑。
- executor.py 支持自定义任务处理、流式响应等。
- card.py 可定义更多技能和元数据。

## 许可证

本示例代码基于 MIT 许可证开源。
