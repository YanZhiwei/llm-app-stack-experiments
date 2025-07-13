"""
配置管理
"""

import os

from langchain_openai import AzureChatOpenAI


class Config:
    """配置管理"""

    def __init__(self):
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_openai_deployment = os.getenv(
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not all([self.azure_openai_api_key, self.azure_openai_endpoint,
                   self.azure_openai_api_version, self.azure_openai_deployment]):
            raise ValueError("Azure OpenAI配置不完整")

    def create_llm(self) -> AzureChatOpenAI:
        """创建LLM实例"""
        return AzureChatOpenAI(
            api_key=self.azure_openai_api_key,
            azure_endpoint=self.azure_openai_endpoint,
            api_version=self.azure_openai_api_version,
            azure_deployment=self.azure_openai_deployment,
            temperature=0.7,
            max_tokens=4000
        )


# 全局配置实例
config = Config()
