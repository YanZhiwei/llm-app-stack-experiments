@echo off
REM LLM App Stack Experiments - Windows 环境设置脚本
REM 使用 micromamba 创建和配置开发环境

echo 🚀 开始设置 LLM App Stack 开发环境...

REM 检查 micromamba 是否已安装
where micromamba >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ micromamba 未安装
    echo 请先安装 micromamba: https://mamba.readthedocs.io/en/latest/installation.html
    pause
    exit /b 1
)

echo ✅ micromamba 已安装

REM 创建环境
echo 📦 创建 micromamba 环境...
micromamba create -f environment.yml -y

REM 激活环境
echo 🔄 激活环境...
call micromamba activate llm-app-stack

echo.
echo 🎉 基础环境设置完成！
echo.
echo 接下来的步骤：
echo 1. 激活环境: micromamba activate llm-app-stack
echo 2. 复制 configs/example.env 到 .env
echo 3. 在 .env 中配置你的 API 密钥
echo 4. 根据学习需要安装依赖包:
echo    - pip install langchain langchain-openai
echo    - pip install jupyter notebook
echo    - pip install streamlit fastapi
echo    - 等等...
echo 5. 开始学习实验！
pause 