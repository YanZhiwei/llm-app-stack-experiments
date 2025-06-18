"""
检查Azure OpenAI环境变量配置
"""

import os

from dotenv import load_dotenv


def check_azure_openai_config():
    """检查Azure OpenAI配置"""
    load_dotenv()

    print("🔍 检查Azure OpenAI配置...")
    print("=" * 40)

    # 检查必需的配置
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if "KEY" in var:
                print(f"✅ {var}: {'*' * 10}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")
            missing_vars.append(var)

    # 检查API版本
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    print(f"📋 AZURE_OPENAI_API_VERSION: {api_version}")

    print("\n" + "=" * 40)
    if missing_vars:
        print("❌ 缺少以下必需的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请检查您的 .env 文件配置")
        return False
    else:
        print("✅ 所有必需的配置都已设置")
        return True


if __name__ == "__main__":
    check_azure_openai_config()
