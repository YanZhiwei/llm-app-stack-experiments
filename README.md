# LLM 应用技术栈学习记录

## 项目概述

这是我的大语言模型应用开发技术栈学习记录项目。用于记录学习过程、实验代码、踩坑经验和技术心得。主要围绕当前主流的LLM应用开发框架进行实践和总结。

## 技术栈

### 核心框架
- **LangChain**: 构建LLM应用的综合框架
- **LangGraph**: 构建有状态的多角色对话应用
- **LlamaIndex**: 专注于数据索引和检索的LLM框架

### 向量数据库
- **Milvus**: 高性能向量数据库
- **Chroma**: 轻量级向量数据库
- **Pinecone**: 云端向量数据库服务

### LLM服务
- **OpenAI API**: GPT系列模型API
- **本地模型**: Ollama, vLLM等本地部署方案

### 其他工具
- **Jupyter Notebook**: 交互式开发环境
- **Streamlit**: 快速构建Web应用
- **FastAPI**: 构建API服务

## 目录结构

```
llm-app-stack-experiments/
│
├── README.md                # 项目概述、学习计划、环境配置
├── pyproject.toml           # 项目配置和依赖管理（uv用）
├── uv.lock                  # 锁定的依赖版本文件
├── .python-version          # Python版本指定
├── docs/                    # 学习笔记、技术总结、踩坑记录
├── notebooks/               # Jupyter 实验和探索
├── scripts/                 # 辅助脚本、工具
├── datasets/                # 实验数据集
├── configs/                 # 配置文件和环境变量模板
├── utils/                   # 通用工具函数
│
├── langchain/               # LangChain 相关实验
├── rag/                     # RAG（检索增强生成）相关实验
├── langgraph/               # LangGraph 相关实验
├── llamaindex/              # LlamaIndex 相关实验
├── agents/                  # 智能体/Agent 相关实验
├── openai/                  # OpenAI API 相关实验
├── milvus/                  # 向量数据库相关实验
│
└── LICENSE                  # 许可证
```

## 环境设置

### 使用 uv 包管理器（推荐）

本项目使用 [uv](https://github.com/astral-sh/uv) 作为 Python 包管理器，提供更快的依赖解析和安装速度。

#### 安装 uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip 安装
pip install uv
```

#### 环境设置

```bash
# 创建虚拟环境并安装依赖
uv venv

# 激活环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装项目依赖
uv pip install -e .

# 或者直接使用 uv 运行（自动管理环境）
uv run python main.py
```

## 配置说明

### 环境变量配置

复制 `configs/example.env` 到 `.env` 并配置API密钥：

```bash
cp configs/example.env .env
# 然后编辑 .env 文件，填入真实的 API 密钥
```

### 常用命令

```bash
# 使用 uv 运行脚本（自动管理环境）
uv run python langchain/xxx.py
uv run python rag/quick_start.py

# 启动 Jupyter Notebook
uv run jupyter notebook notebooks/

# 添加新依赖
uv add package_name

# 移除依赖
uv remove package_name

# 更新依赖
uv lock --upgrade

# 查看项目信息
uv tree
```

## 学习笔记

- `docs/` 目录记录学习过程中的技术笔记和心得
- `notebooks/` 目录用于交互式实验和探索
- 各个技术栈目录记录对应的实验代码和实践总结

## 许可证

MIT License - 个人学习项目 