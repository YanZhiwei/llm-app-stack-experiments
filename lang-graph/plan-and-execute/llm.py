from langchain_openai import AzureChatOpenAI

from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


class LLM:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,  # type: ignore
            temperature=0.2,
        )

    def chat(self, messages):
        # messages: [{"role": "system", ...}, {"role": "user", ...}]
        return self.llm.invoke(messages).content.strip()

    def stream(self, messages):
        # 流式生成器，直接返回 langchain 的流式生成器
        return self.llm.stream(messages)

# 用法示例：
# if __name__ == "__main__":
#     llm = LLM()
#     result = llm.chat([
#         {"role": "system", "content": "你是一个规划助手。"},
#         {"role": "user", "content": "帮我制定一个学习Python的计划。"}
#     ])
#     print(result) 