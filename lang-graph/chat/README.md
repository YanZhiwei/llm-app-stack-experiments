# LangGraph 流式聊天应用

这是一个基于LangGraph和React的流式聊天应用，支持实时流式输出AI响应。

## 项目结构

```
chat/
├── backend/          # LangGraph后端
│   ├── main.py      # FastAPI应用
│   ├── check_config.py  # 配置检查脚本
│   ├── azure_config_example.env  # Azure OpenAI配置示例
│   ├── env.example  # 环境变量示例
│   ├── uv.lock      # 依赖锁定文件
│   └── pyproject.toml
└── frontend/        # React前端
    ├── src/
    │   ├── App.js
    │   ├── App.css
    │   ├── index.js
    │   └── index.css
    ├── public/
    │   └── index.html
    ├── package.json
    └── package-lock.json
```

## 功能特性

- 🚀 基于LangGraph的智能对话流程
- 💬 实时流式输出AI响应
- 🎨 现代化的React UI界面
- 📱 响应式设计，支持移动端
- 🔄 对话历史管理
- 🗑️ 一键清空对话

## 快速开始

### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
uv venv

# 安装依赖
uv pip install langgraph langchain langchain-openai fastapi uvicorn pydantic python-multipart sse-starlette python-dotenv

# 锁定依赖，生成 uv.lock 文件（推荐）
uv lock

# 设置环境变量
# 复制 env.example 为 .env 并填入您的Azure OpenAI配置
cp env.example .env
# 编辑 .env 文件，填入您的 Azure OpenAI 配置

# 检查配置（可选，推荐）
python check_config.py

# 启动后端服务
python main.py
```

后端将在 `http://localhost:8000` 启动。

### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端将在 `http://localhost:3000` 启动。

## 环境变量配置

在 `backend/.env` 文件中配置以下环境变量：

```env
# Azure OpenAI配置
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

### 配置说明

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI资源端点
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API密钥
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`: 部署名称
- `AZURE_OPENAI_API_VERSION`: API版本（可选，默认为最新版本）

> **说明：** 项目依赖 `python-dotenv` 自动加载 `.env` 文件，无需手动导入。

## 后端依赖与环境管理

- 推荐使用 [uv](https://github.com/astral-sh/uv) 工具进行 Python 环境和依赖管理。
- 依赖锁定文件为 `uv.lock`，可通过 `uv lock` 生成，确保环境一致性。
- 复现环境时，先运行 `uv venv`，再 `uv pip install -r uv.lock`。

## 配置检查

- 使用 `check_config.py` 脚本可快速检查 Azure OpenAI 相关环境变量是否配置正确，避免运行时错误。
- 推荐在首次部署和每次修改配置后运行该脚本。

## API端点

### 聊天相关

- `POST /chat` - 发送聊天消息（非流式）
- `GET /chat/stream` - 流式聊天端点（SSE，适合 EventSource 用法）
- `POST /chat/stream` - 流式聊天端点（推荐，适合 fetch+流式拼接，前端已采用此方式）
- `GET /conversations/{conversation_id}` - 获取对话历史
- `DELETE /conversations/{conversation_id}` - 删除对话

### 配置相关

- `GET /config/status` - 获取当前配置状态（检查API密钥和配置是否完整）

### 流式响应格式

#### SSE (GET)

```javascript
const eventSource = new EventSource('/chat/stream?message=你好&conversation_id=default');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data.content);
};
eventSource.addEventListener('complete', (event) => {
  console.log('响应完成');
  eventSource.close();
});
```

#### fetch+流 (POST，推荐)

```javascript
const response = await fetch('/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: '你好', conversation_id: 'default' })
});
const reader = response.body.getReader();
const decoder = new TextDecoder();
let done = false;
while (!done) {
  const { value, done: streamDone } = await reader.read();
  if (value) {
    const chunk = decoder.decode(value, { stream: true });
    // 处理 chunk
  }
  done = streamDone;
}
```

## 技术栈

### 后端
- **LangGraph**: 对话流程管理
- **LangChain**: LLM集成
- **FastAPI**: Web框架
- **SSE-Starlette**: 服务器发送事件
- **Pydantic**: 数据验证

### 前端
- **React**: UI框架
- **Axios**: HTTP客户端
- **Lucide React**: 图标库
- **CSS3**: 样式和动画

## 开发说明

### 后端开发

1. LangGraph图结构：
   - 使用`StateGraph`管理对话状态
   - 通过`MemorySaver`持久化对话历史
   - 支持异步流式处理

2. 流式输出：
   - 使用`EventSourceResponse`实现SSE
   - 支持实时流式文本输出
   - 错误处理和连接管理

### 前端开发

1. 状态管理：
   - 使用React Hooks管理组件状态
   - 实时更新流式消息
   - 自动滚动到最新消息

2. UI设计：
   - 现代化渐变设计
   - 响应式布局
   - 流畅的动画效果

## 部署

### 后端部署

```bash
# 生产环境启动
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

```bash
# 构建生产版本
npm run build

# 部署到静态服务器
# 将 build/ 目录部署到您的Web服务器
```

## Azure OpenAI 使用指南

### 1. 获取Azure OpenAI资源

1. 登录 [Azure门户](https://portal.azure.com)
2. 创建或选择现有的Azure OpenAI资源
3. 在"模型部署"页面部署您需要的模型（如gpt-4o-mini）
4. 在"密钥和终结点"页面获取API密钥和端点URL

### 2. 配置环境变量

复制 `azure_config_example.env` 为 `.env`：

```bash
cp azure_config_example.env .env
```

编辑 `.env` 文件，填入您的Azure OpenAI配置：

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. 验证配置

运行配置检查脚本：

```bash
python check_config.py
```

### 4. 启动应用

```bash
python main.py
```

## 注意事项

1. 确保设置了正确的Azure OpenAI API密钥
2. 后端和前端需要同时运行
3. Azure OpenAI需要有效的Azure订阅和资源
4. 确保模型部署名称正确
5. 生产环境建议使用HTTPS

## 许可证

MIT License 