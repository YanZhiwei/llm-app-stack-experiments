# Plan-and-Execute (基于 langgraph)

## 项目简介
本项目实现了基于 langgraph 的 Plan-and-Execute 智能体结构，模型后端采用 AzureOpenAI gpt-4o-min。

## 目录结构
```
plan-and-execute/
  plan.py
  executor.py
  memory.py
  tools.py
  config.py
  main.py
  __init__.py
  api/
    __init__.py
    main.py
    models.py
  README.md
  pyproject.toml
  uv.lock
```

## 环境管理
本项目使用 [uv](https://github.com/astral-sh/uv) 进行 Python 依赖和虚拟环境管理。

### 安装依赖
```bash
uv venv
uv pip install -r uv.lock
```

如需更新依赖：
```bash
uv pip install <package>
uv lock
```

## 运行方式

### 命令行版本
请在配置好 AzureOpenAI API Key 和 Endpoint 后，运行：
```bash
python main.py
```

### API 服务版本
启动 FastAPI 服务：
```bash
python api/main.py
```

服务启动后，可通过以下方式调用：

#### 1. 访问 API 文档
打开浏览器访问：http://localhost:8000/docs

#### 2. 调用接口
```bash
curl -X POST "http://localhost:8000/plan-and-execute" \
     -H "Content-Type: application/json" \
     -d '{"goal": "学习Python编程"}'
```

#### 3. Python 调用示例
```python
import requests

response = requests.post(
    "http://localhost:8000/plan-and-execute",
    json={"goal": "学习Python编程"}
)
result = response.json()
print(result)
```

## 主要依赖
- langgraph
- langchain-openai
- fastapi
- uvicorn
