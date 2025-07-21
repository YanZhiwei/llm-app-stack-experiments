#!/usr/bin/env python3
"""
配置检查脚本
用于验证Azure OpenAI配置是否正确
"""

import os
import sys

from dotenv import load_dotenv


def load_env_file():
    """加载.env文件"""
    env_file = ".env"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ 已加载 {env_file} 文件")
    else:
        print(f"⚠️  未找到 {env_file} 文件，使用系统环境变量")

def check_azure_openai_config():
    """检查Azure OpenAI配置"""
    print("\n🔍 检查Azure OpenAI配置...")
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    config_items = [
        ("端点", endpoint),
        ("API密钥", api_key),
        ("部署名称", deployment_name)
    ]
    
    all_configured = True
    for name, value in config_items:
        if value:
            print(f"✅ {name}: {value}")
        else:
            print(f"❌ {name}: 未配置")
            all_configured = False
    
    print(f"✅ API版本: {api_version}")
    
    return all_configured

def main():
    """主函数"""
    print("🚀 LangGraph聊天应用配置检查工具")
    print("=" * 50)
    
    # 加载环境变量
    load_env_file()
    
    print("\n📋 当前配置: Azure OpenAI")
    is_configured = check_azure_openai_config()
    
    print("\n" + "=" * 50)
    
    if is_configured:
        print("🎉 配置检查通过！可以启动应用了。")
        print("\n启动命令:")
        print("python main.py")
        return 0
    else:
        print("❌ 配置不完整，请检查环境变量。")
        print("\n配置说明:")
        print("1. 配置 AZURE_OPENAI_ENDPOINT")
        print("2. 配置 AZURE_OPENAI_API_KEY")
        print("3. 配置 AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 