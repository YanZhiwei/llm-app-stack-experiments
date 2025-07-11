# Super Agent

## 项目简介

Super Agent 是一个基于 [LangGraph](https://github.com/langchain-ai/langgraph) 和 [LangChain](https://github.com/langchain-ai/langchain) 的多智能体编排实验项目，支持任务规划、工具调用与自动执行。

## 主要功能
- 任务规划与分解
- 工具自动调用（如网络搜索、数据分析）
- 多 agent 协作执行
- 状态追踪与推理日志

## 依赖环境
- Python 3.12
- [LangChain](https://pypi.org/project/langchain/) >= 0.3.26
- [LangGraph](https://pypi.org/project/langgraph/) >= 0.5.2
- 推荐使用 [uv](https://github.com/astral-sh/uv) 进行依赖和环境管理

## 安装与运行

1. **克隆仓库**

```bash
git clone <your-repo-url>
cd super-agent
```

2. **创建虚拟环境并安装依赖**

推荐使用 uv：

```bash
uv venv
uv pip install -r uv.lock
```

如需重新生成依赖锁定文件：

```bash
uv lock
```

3. **运行示例**

```bash
python main.py
```

## 核心文件说明

- `main.py`：程序入口，初始化 orchestrator，定义初始状态并运行工作流。
- `orchestrator.py`：定义 SuperAgentOrchestrator，负责构建多 agent 工作流（planner → tools → executor）。
- `agents.py`：包含 planner_agent（任务规划）和 executor_agent（执行工具结果）。
- `tools.py`：定义可用工具（如 web_search、analyze_data）及工具注册方法。
- `state.py`：定义 SuperAgentState 状态结构。

## 状态结构（SuperAgentState）

```python
class SuperAgentState(TypedDict):
    messages: List[BaseMessage]         # 消息历史
    current_task: str                   # 当前任务描述
    task_plan: List[str]                # 任务分解计划
    collected_data: Dict[str, Any]      # 收集到的数据
    reasoning_log: List[str]            # 推理与决策日志
    next_action: str                    # 下一步动作
    tools_used: List[str]               # 已用工具
    final_result: str                   # 最终结果
```

## Agent 与工具简介

- **planner_agent**：负责根据当前状态规划下一步任务，决定是否调用工具。
- **executor_agent**：处理工具调用结果，生成最终输出。
- **工具（tools）**：
  - `web_search(query: str)`：模拟网络搜索。
  - `analyze_data(data: str)`：模拟数据分析。

## 工作流示意

planner → tools → executor → END

## 参考
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 官方文档](https://python.langchain.com/)
