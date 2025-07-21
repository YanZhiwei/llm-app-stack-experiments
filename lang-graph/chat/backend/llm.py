import logging
import os

from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)

def create_llm():
    """创建Azure OpenAI LLM实例"""
    # Azure OpenAI配置
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    logger.info(f"[配置] Azure OpenAI: endpoint={azure_endpoint}, deployment={deployment_name}, version={api_version}")
    
    if not all([azure_endpoint, azure_api_key, deployment_name]):
        logger.error("Azure OpenAI配置不完整，请检查环境变量")
        raise ValueError("Azure OpenAI配置不完整，请检查环境变量")
    
    return AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=deployment_name,
        api_version=api_version,
        api_key=azure_api_key,
        temperature=0.7,
        streaming=True
    )

def get_llm_config():
    """获取LLM配置信息"""
    return {
        "service": "Azure OpenAI",
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        "api_key_configured": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    } 