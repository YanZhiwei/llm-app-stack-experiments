# Azure OpenAI + Tavily Fullstack LangGraph Quickstart

本项目演示了一个完整的全栈应用，前端为 React，后端为基于 LangGraph 的智能体，支持多轮自动化研究、网络检索和答案生成。后端智能体基于 Azure OpenAI（如 gpt-4o-mini）进行推理，结合 Tavily 搜索引擎进行高质量网页检索，具备反思和多轮知识补全能力，最终生成带有引用的结构化答案。

<img src="./app.png" title="Fullstack LangGraph" alt="Fullstack LangGraph" width="90%">

## Features

- 💬 全栈应用，React 前端 + LangGraph 后端。
- 🧠 LangGraph 智能体，支持多轮推理与研究。
- 🔍 动态搜索查询生成，基于 Azure OpenAI。
- 🌐 高质量网页检索，集成 Tavily API。
- 🤔 反思与知识缺口分析，自动生成后续查询。
- 📄 结构化答案，带引用来源。
- 🔄 前后端热重载，便于开发。

## Project Structure

- `frontend/`: Vite + React 前端。
- `backend/`: LangGraph/FastAPI 后端，包含研究智能体核心逻辑。

## Getting Started: Development and Local Testing

**1. Prerequisites:**

- Node.js 和 npm (或 yarn/pnpm)
- Python 3.11+
- **Azure OpenAI 相关环境变量**：
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_VERSION`
  - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`
- **Tavily 搜索 API Key**：
  - `TAVILY_API_KEY`

在 `backend/` 目录下创建 `.env` 文件，内容示例：

```env
AZURE_OPENAI_API_KEY=你的key
AZURE_OPENAI_ENDPOINT=https://你的资源名.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=你的实际deployment名
TAVILY_API_KEY=你的tavily-key
```

**2. Install Dependencies:**

**Backend:**

```bash
cd backend
pip install .
```

**Frontend:**

```bash
cd frontend
npm install
```

**3. Run Development Servers:**

```bash
make dev
```

前后端开发服务器将自动启动。前端默认地址为 `http://localhost:5173/app`。

_也可分别运行：_

- 后端：`langgraph dev`（默认 `http://127.0.0.1:2024`）
- 前端：`npm run dev`（默认 `http://localhost:5173`）

## How the Backend Agent Works (High-Level)

核心智能体定义在 `backend/src/agent/graph.py`，主要流程如下：

<img src="./agent.png" title="Agent Flow" alt="Agent Flow" width="50%">

1.  **生成初始查询**：基于用户输入，使用 Azure OpenAI 生成多条高质量搜索查询。
2.  **网络检索**：每条查询通过 Tavily API 检索网页，获取高质量内容。
3.  **反思与知识缺口分析**：智能体分析检索结果，判断信息是否充分，若有缺口则生成后续查询。
4.  **多轮迭代**：如有知识缺口，自动进入下一轮查询-检索-反思，直至信息充分或达到最大轮数。
5.  **生成结构化答案**：信息充分后，智能体用 Azure OpenAI 综合所有检索内容，生成带引用的结构化答案。

## CLI Example

可直接用命令行运行智能体：

```bash
cd backend
python examples/cli_research.py "人工智能在医疗诊断中的应用"
```

## Deployment

生产环境下，后端可同时服务前端静态文件。LangGraph 需依赖 Redis 和 Postgres。

**环境变量**：请确保所有 Azure OpenAI 和 Tavily 相关变量已配置。

**Docker 部署示例**：

```bash
docker build -t aoai-tavily-langgraph -f Dockerfile .
AZURE_OPENAI_API_KEY=... TAVILY_API_KEY=... docker-compose up
```

## Technologies Used

- [React](https://reactjs.org/) (with [Vite](https://vitejs.dev/)) - 前端 UI
- [Tailwind CSS](https://tailwindcss.com/) - 样式
- [Shadcn UI](https://ui.shadcn.com/) - 组件
- [LangGraph](https://github.com/langchain-ai/langgraph) - 后端智能体编排
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM 推理与生成
- [Tavily](https://www.tavily.com/) - 高级网页检索

## License

本项目采用 Apache License 2.0，详见 [LICENSE](LICENSE)。

## Reference

本项目基于 [google-gemini/gemini-fullstack-langgraph-quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) 改造和扩展，原始项目由 Google Gemini 团队开源，采用 Apache-2.0 协议。
