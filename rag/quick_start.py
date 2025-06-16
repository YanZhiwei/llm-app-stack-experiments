"""
RAG 快速开始示例
使用内存向量存储和示例数据，快速体验RAG功能
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 加载环境变量
load_dotenv()

# 示例文档数据
SAMPLE_DOCUMENTS = [
    """
    人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
    AI包括机器学习、深度学习、自然语言处理、计算机视觉等多个子领域。
    """,
    """
    机器学习是人工智能的一个子集，它使计算机能够从数据中自动学习和改进，而无需明确编程。
    机器学习算法包括监督学习、无监督学习和强化学习。
    """,
    """
    深度学习是机器学习的一个子集，使用具有多个层的神经网络来模拟人脑的学习过程。
    深度学习在图像识别、语音识别和自然语言处理等领域取得了重大突破。
    """,
    """
    自然语言处理（NLP）是人工智能领域的一个重要分支，专注于让计算机理解、解释和生成人类语言。
    NLP技术包括文本分析、情感分析、机器翻译、问答系统等。
    """,
    """
    大语言模型（LLM）如GPT-4是基于Transformer架构的深度学习模型，能够理解和生成人类语言。
    这些模型通过在大量文本数据上进行预训练，具备了强大的语言理解和生成能力。
    """
]

def create_quick_rag():
    """创建快速RAG系统"""
    
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("请设置OPENAI_API_KEY环境变量")
    
    print("正在初始化RAG系统...")
    
    # 1. 初始化模型和嵌入
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    # 2. 创建文档对象
    documents = [Document(page_content=doc.strip()) for doc in SAMPLE_DOCUMENTS]
    
    # 3. 创建向量存储（使用FAISS内存存储）
    print("正在创建向量存储...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # 4. 创建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 5. 创建提示模板
    template = """基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明不知道。

上下文：
{context}

问题：{question}

回答："""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # 6. 创建RAG链
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("RAG系统初始化完成！")
    return rag_chain, retriever

def main():
    """主函数"""
    try:
        # 创建RAG系统
        rag_chain, retriever = create_quick_rag()
        
        # 示例问题
        sample_questions = [
            "什么是人工智能？",
            "机器学习和深度学习有什么区别？",
            "大语言模型是什么？",
            "自然语言处理有哪些应用？"
        ]
        
        print("\n" + "="*60)
        print("RAG快速开始示例")
        print("="*60)
        
        # 运行示例问题
        for i, question in enumerate(sample_questions, 1):
            print(f"\n示例 {i}: {question}")
            print("-" * 40)
            
            # 获取相关文档
            relevant_docs = retriever.get_relevant_documents(question)
            print(f"检索到 {len(relevant_docs)} 个相关文档片段")
            
            # 生成回答
            answer = rag_chain.invoke(question)
            print(f"回答: {answer}")
        
        # 交互式问答
        print(f"\n{'='*60}")
        print("现在您可以提问了！输入 'quit' 退出")
        print("="*60)
        
        while True:
            question = input("\n请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
                
            if not question:
                continue
            
            try:
                answer = rag_chain.invoke(question)
                print(f"回答: {answer}")
            except Exception as e:
                print(f"生成回答时出错: {e}")
                
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 