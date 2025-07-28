import os
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """代理的配置。"""

    query_generator_model: str = Field(
        default="gemini-2.0-flash",
        description="用于代理查询生成的语言模型名称。"
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash",
        description="用于代理反思的语言模型名称。"
    )

    answer_model: str = Field(
        default="gemini-2.5-pro",
        description="用于代理回答的语言模型名称。"
    )

    number_of_initial_queries: int = Field(
        default=3,
        description="要生成的初始搜索查询数量。"
    )

    max_research_loops: int = Field(
        default=2,
        description="要执行的最大研究循环数。"
    )

    # Azure OpenAI 配置
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API Key"
    )
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI Endpoint"
    )
    azure_openai_api_version: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API Version"
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI Chat Deployment Name"
    )
    # Tavily 配置
    tavily_api_key: Optional[str] = Field(
        default=None,
        description="Tavily API Key"
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """从 RunnableConfig 创建 Configuration 实例。"""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # 从环境或配置获取原始值
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        # 兼容 AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        if not raw_values.get("azure_openai_deployment"):
            raw_values["azure_openai_deployment"] = os.environ.get(
                "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

        # 过滤掉 None 值
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
