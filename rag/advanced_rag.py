"""
高级RAG系统示例
包含流式响应、多种检索策略、重排序、和高级文档处理功能
"""

import os
import asyncio
from typing import List, Dict, Any, AsyncIterator
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.callbacks import StreamingStdOutCallbackHandler

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever

# 加载环境变量
load_dotenv()

class AdvancedRAGSystem:
    """高级RAG系统"""
    
    def __init__(self, 
                 model_name: str = "gpt-4", 
                 temperature: float = 0.1,
                 streaming: bool = True):
        """
        初始化高级RAG系统
        
        Args:
            model_name: OpenAI模型名称
            temperature: 生成温度
            streaming: 是否启用流式响应
        """
        self.model_name = model_name
        self.temperature = temperature
        self.streaming = streaming
        
        # 初始化回调处理器
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        
        # 初始化OpenAI组件
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )
        
        # 初始化高级文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.vectorstore = None
        self.retriever = None
        self.compression_retriever = None
        self.rag_chain = None
    
    def load_documents_advanced(self, documents_path: str) -> List[Document]:
        """
        高级文档加载 - 支持多种文件格式
        
        Args:
            documents_path: 文档路径
            
        Returns:
            加载的文档列表
        """
        documents = []
        
        if os.path.isfile(documents_path):
            # 根据文件扩展名选择合适的加载器
            if documents_path.endswith('.pdf'):
                loader = PyPDFLoader(documents_path)
            elif documents_path.endswith('.md'):
                loader = UnstructuredMarkdownLoader(documents_path)
            else:
                # 默认使用文本加载器
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(documents_path, encoding='utf-8')
            
            documents = loader.load()
        
        elif os.path.isdir(documents_path):
            # 遍历目录加载多种文件类型
            for root, dirs, files in os.walk(documents_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if file.endswith('.pdf'):
                            loader = PyPDFLoader(file_path)
                        elif file.endswith('.md'):
                            loader = UnstructuredMarkdownLoader(file_path)
                        elif file.endswith('.txt'):
                            from langchain_community.document_loaders import TextLoader
                            loader = TextLoader(file_path, encoding='utf-8')
                        else:
                            continue
                        
                        docs = loader.load()
                        documents.extend(docs)
                    except Exception as e:
                        print(f"加载文件 {file_path} 时出错: {e}")
        
        print(f"成功加载 {len(documents)} 个文档")
        return documents
    
    def create_hybrid_retriever(self, documents: List[Document]) -> None:
        """
        创建混合检索器（向量检索 + BM25检索）
        
        Args:
            documents: 文档列表
        """
        print("正在创建混合检索器...")
        
        # 创建向量存储
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory="./advanced_chroma_db"
        )
        
        # 创建向量检索器
        vector_retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6}
        )
        
        # 创建BM25检索器
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 6
        
        # 创建集成检索器
        self.retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.7, 0.3]  # 向量检索权重更高
        )
        
        # 创建压缩检索器（用于重排序和过滤）
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.retriever
        )
        
        print("混合检索器创建完成")
    
    def create_advanced_rag_chain(self) -> None:
        """创建高级RAG链"""
        # 高级提示模板
        template = """你是一个专业的AI助手。请基于以下上下文信息详细回答用户的问题。

注意事项：
1. 仔细分析上下文信息，提供准确、详细的回答
2. 如果上下文信息不足以完全回答问题，请明确指出
3. 引用相关的上下文信息来支持你的回答
4. 保持回答的逻辑性和连贯性

上下文信息：
{context}

问题：{question}

详细回答："""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            formatted = []
            for i, doc in enumerate(docs, 1):
                content = doc.page_content.strip()
                source = getattr(doc.metadata, 'source', '未知来源')
                formatted.append(f"[文档{i}] (来源: {source})\n{content}")
            return "\n\n".join(formatted)
        
        # 创建高级RAG链
        self.rag_chain = (
            {
                "context": self.compression_retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("高级RAG链创建完成")
    
    async def aquery(self, question: str) -> str:
        """
        异步查询RAG系统
        
        Args:
            question: 用户问题
            
        Returns:
            生成的回答
        """
        if self.rag_chain is None:
            raise ValueError("RAG链尚未创建")
        
        print(f"\n🔍 问题: {question}")
        print("正在检索相关信息...")
        
        # 获取相关文档
        relevant_docs = await self.compression_retriever.aget_relevant_documents(question)
        print(f"✅ 检索到 {len(relevant_docs)} 个高质量文档片段")
        
        if self.streaming:
            print("\n🤖 AI回答：")
            print("-" * 50)
            
        # 生成回答
        answer = await self.rag_chain.ainvoke(question)
        return answer
    
    def query_with_sources(self, question: str) -> Dict[str, Any]:
        """
        查询并返回带来源的回答
        
        Args:
            question: 用户问题
            
        Returns:
            包含回答和来源的字典
        """
        if self.compression_retriever is None:
            raise ValueError("检索器尚未创建")
        
        # 获取相关文档
        relevant_docs = self.compression_retriever.get_relevant_documents(question)
        
        # 格式化上下文
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # 生成回答
        answer = self.rag_chain.invoke(question)
        
        # 提取来源信息
        sources = []
        for doc in relevant_docs:
            source_info = {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }
    
    def setup_advanced(self, documents_path: str) -> None:
        """
        完整设置高级RAG系统
        
        Args:
            documents_path: 文档路径
        """
        print("🚀 开始设置高级RAG系统...")
        
        # 1. 加载文档
        documents = self.load_documents_advanced(documents_path)
        
        # 2. 处理文档
        processed_docs = self.text_splitter.split_documents(documents)
        print(f"文档分割为 {len(processed_docs)} 个片段")
        
        # 3. 创建混合检索器
        self.create_hybrid_retriever(processed_docs)
        
        # 4. 创建RAG链
        self.create_advanced_rag_chain()
        
        print("✅ 高级RAG系统设置完成！")


async def main():
    """主函数"""
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置OPENAI_API_KEY环境变量")
        return
    
    # 创建高级RAG系统
    rag = AdvancedRAGSystem(
        model_name="gpt-4",
        temperature=0.1,
        streaming=True
    )
    
    # 示例：使用示例文档目录
    sample_docs_path = "sample_docs"
    
    try:
        # 设置RAG系统
        rag.setup_advanced(sample_docs_path)
        
        # 示例问题
        sample_questions = [
            "请详细解释人工智能的发展历史",
            "机器学习有哪些主要算法类型？",
            "深度学习在计算机视觉中有什么应用？"
        ]
        
        print("\n" + "="*70)
        print("🎯 高级RAG系统演示")
        print("="*70)
        
        # 运行示例问题
        for i, question in enumerate(sample_questions, 1):
            print(f"\n📝 示例 {i}:")
            try:
                await rag.aquery(question)
                print("\n" + "-"*50)
            except Exception as e:
                print(f"❌ 处理问题时出错: {e}")
        
        # 交互式查询
        print(f"\n{'='*70}")
        print("💬 交互式问答模式 (输入 'quit' 退出)")
        print("="*70)
        
        while True:
            question = input("\n请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not question:
                continue
            
            try:
                await rag.aquery(question)
                print("\n" + "-"*50)
            except Exception as e:
                print(f"❌ 生成回答时出错: {e}")
    
    except Exception as e:
        print(f"❌ 设置RAG系统时出错: {e}")
        print("\n💡 提示: 请确保存在示例文档目录或修改文档路径")


if __name__ == "__main__":
    asyncio.run(main()) 