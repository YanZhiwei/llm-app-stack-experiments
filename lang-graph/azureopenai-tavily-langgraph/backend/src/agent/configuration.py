import os
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-2.0-flash",
        description="The name of the language model to use for the agent's query generation."
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash",
        description="The name of the language model to use for the agent's reflection."
    )

    answer_model: str = Field(
        default="gemini-2.5-pro",
        description="The name of the language model to use for the agent's answer."
    )

    number_of_initial_queries: int = Field(
        default=3,
        description="The number of initial search queries to generate."
    )

    max_research_loops: int = Field(
        default=2,
        description="The maximum number of research loops to perform."
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
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        # 兼容 AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        if not raw_values.get("azure_openai_deployment"):
            raw_values["azure_openai_deployment"] = os.environ.get(
                "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
