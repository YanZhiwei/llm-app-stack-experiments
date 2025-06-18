"""
基于OpenAI的RAG (Retrieval-Augmented Generation) 入门示例

这个示例展示了如何：
1. 加载和处理文档
2. 创建向量数据库
3. 实现检索增强生成
4. 使用OpenAI的GPT-4和Embeddings
"""

import os
from typing import Any, List, Optional

from check_env import check_azure_openai_config
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载环境变量
load_dotenv()


class RAGSystem:
    """RAG系统主类"""

    def __init__(self, model_name: str,
                 api_version: str,
                 temperature: float = 0.1):
        """
        初始化RAG系统

        Args:
            model_name: OpenAI模型名称
            temperature: 生成温度参数
        """
        self.model_name = model_name
        self.temperature = temperature

        # 初始化OpenAI组件
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv(
                "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini"),
            temperature=temperature,
            api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )

        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME",
                                       "text-embedding-3-large")
        )

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            add_start_index=True
        )

        self.vectorstore = None
        self.retriever: Optional[Any] = None
        self.rag_chain: Optional[Any] = None

    def load_documents(self, documents_path: str) -> List[Document]:
        """
        加载文档

        Args:
            documents_path: 文档路径（文件或目录）

        Returns:
            加载的文档列表
        """
        if os.path.isfile(documents_path):
            # 加载单个文件
            loader = TextLoader(documents_path, encoding='utf-8')
            documents = loader.load()
        elif os.path.isdir(documents_path):
            # 加载目录中的所有txt文件
            loader = DirectoryLoader(
                documents_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            documents = loader.load()
        else:
            raise ValueError(f"路径不存在: {documents_path}")

        print(f"成功加载 {len(documents)} 个文档")
        return documents

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        处理和分割文档

        Args:
            documents: 原始文档列表

        Returns:
            分割后的文档片段列表
        """
        # 分割文档
        splits = self.text_splitter.split_documents(documents)
        print(f"文档分割为 {len(splits)} 个片段")
        return splits

    def create_vectorstore(self, documents: List[Document]) -> None:
        """
        创建向量数据库

        Args:
            documents: 文档列表
        """
        print("正在创建向量数据库...")
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory="./chroma_db"  # 持久化存储
        )

        # 创建检索器
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6}  # 返回最相似的6个文档片段
        )
        print("向量数据库创建完成")

    def create_rag_chain(self) -> None:
        """创建RAG链"""
        if self.retriever is None:
            raise ValueError("检索器尚未初始化，请先调用create_vectorstore方法")

        # 定义提示模板
        template = """你是一个有用的AI助手。请基于以下上下文信息回答用户的问题。
        如果上下文中没有相关信息，请说明你不知道答案。

        上下文信息:
        {context}

        问题: {question}

        回答:"""

        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # 创建RAG链 - 使用LangChain的管道操作符构建检索增强生成流程
        # 1. 输入处理：将用户问题传递给检索器和问题字段
        # 2. 检索增强：从向量数据库检索相关文档并格式化为上下文
        # 3. 提示工程：将上下文和问题组合成结构化提示
        # 4. 模型推理：使用大语言模型生成回答
        # 5. 输出解析：将模型输出转换为字符串格式
        self.rag_chain = (
            {
                "context": self.retriever | format_docs,  # 检索相关文档并格式化为上下文
                "question": RunnablePassthrough()         # 直接传递用户问题，不做任何修改
            }
            | prompt                                      # 应用提示模板
            | self.llm                                    # 使用大语言模型生成回答
            | StrOutputParser()                          # 解析输出为字符串
        )
        print("RAG链创建完成")

    def query(self, question: str) -> str:
        """
        查询RAG系统

        Args:
            question: 用户问题

        Returns:
            生成的回答
        """
        if self.rag_chain is None:
            raise ValueError("RAG链尚未创建，请先调用setup方法")

        if self.retriever is None:
            raise ValueError("检索器尚未初始化")

        print(f"\n问题: {question}")
        print("正在生成回答...")

        # 获取相关文档
        relevant_docs = self.retriever.invoke(question)
        print(f"找到 {len(relevant_docs)} 个相关文档片段")

        # 生成回答
        answer = self.rag_chain.invoke(question)
        return answer

    def setup(self, documents_path: str) -> None:
        """
        完整设置RAG系统

        Args:
            documents_path: 文档路径
        """
        print("开始设置RAG系统...")

        # 1. 加载文档
        documents = self.load_documents(documents_path)

        # 2. 处理文档
        processed_docs = self.process_documents(documents)

        # 3. 创建向量数据库
        self.create_vectorstore(processed_docs)

        # 4. 创建RAG链
        self.create_rag_chain()

        print("RAG系统设置完成！")


def main():
    """主函数 - 演示RAG系统的使用"""
    # 禁用LangSmith跟踪以避免403错误
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    check_azure_openai_config()

    # 获取API版本，如果没有设置则使用默认值
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # 创建RAG系统
    rag = RAGSystem(model_name="gpt-4",
                    api_version=api_version, temperature=0.1)

    # 示例：使用示例文档
    sample_docs_path = "rag/sample_docs"

    try:
        # 设置RAG系统
        rag.setup(sample_docs_path)

        # 交互式查询
        print("\n" + "="*50)
        print("RAG系统已准备就绪！")
        print("输入 'quit' 或 'exit' 退出程序")
        print("="*50)

        while True:
            question = input("\n请输入您的问题: ").strip()

            if question.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break

            if not question:
                continue

            try:
                answer = rag.query(question)
                print(f"\n回答: {answer}")
            except Exception as e:
                print(f"生成回答时出错: {e}")

    except Exception as e:
        print(f"设置RAG系统时出错: {e}")
        print("\n提示: 请确保存在示例文档目录或修改文档路径")


if __name__ == "__main__":
    main()
