print("=== 当前main.py已加载，流式推理版本 ===")
import asyncio
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from llm import create_llm, get_llm_config
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)



app = FastAPI(title="LangGraph Streaming Chat API")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义状态类型
class ChatState(BaseModel):
    messages: list = []
    current_message: str = ""
    is_complete: bool = False

# 创建LLM实例
llm = create_llm()

# 定义节点函数
def generate_response(state: ChatState) -> ChatState:
    """生成AI响应"""
    messages = state.messages
    if not messages:
        return state
    user_message = messages[-1]["content"]
    conversation = []
    for msg in messages[:-1]:
        if msg["role"] == "user":
            conversation.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            conversation.append({"role": "assistant", "content": msg["content"]})
    conversation.append({"role": "user", "content": user_message})
    logger.info("[流程] 调用LLM生成响应，历史消息数: %d", len(conversation))
    try:
        response = llm.invoke(conversation)
        logger.info("[流程] LLM响应生成完毕")
    except Exception as e:
        logger.error(f"[异常] LLM调用失败: {e}")
        raise
    state.messages.append({
        "role": "assistant",
        "content": response.content
    })
    state.current_message = response.content
    state.is_complete = True
    return state

# 创建LangGraph
workflow = StateGraph(ChatState)
workflow.add_node("generate_response", generate_response)
workflow.set_entry_point("generate_response")
workflow.add_edge("generate_response", END)
app_graph = workflow.compile(checkpointer=MemorySaver())

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    message: str
    conversation_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"[API] /chat 收到请求，conversation_id={request.conversation_id}")
    try:
        config = {"configurable": {"thread_id": request.conversation_id}}
        current_state = await app_graph.aget_state(config)
        messages = current_state.values.get("messages", [])
        messages.append({
            "role": "user",
            "content": request.message
        })
        new_state = ChatState(messages=messages)
        logger.info("[流程] 开始LangGraph推理")
        result = await app_graph.ainvoke(new_state, config)
        logger.info("[流程] LangGraph推理完成")
        return ChatResponse(
            message=result["current_message"],
            conversation_id=request.conversation_id
        )
    except Exception as e:
        logger.error(f"[异常] /chat 处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/stream")
async def chat_stream(message: str, conversation_id: str = "default"):
    logger.info(f"[API] /chat/stream 收到请求，conversation_id={conversation_id}")
    async def generate_stream() -> AsyncGenerator[Dict[str, Any], None]:
        try:
            import pprint

            # 获取历史消息
            config = {"configurable": {"thread_id": conversation_id}}
            current_state = await app_graph.aget_state(config)
            messages = current_state.values.get("messages", [])
            messages.append({
                "role": "user",
                "content": message
            })
            logger.info("[流程] 开始LLM token流式推理")
            full_content = ""
            async for chunk in llm.astream(messages):
                logger.info(f"[调试] chunk repr: {repr(chunk)}")
                if hasattr(chunk, "__dict__"):
                    logger.info(f"[调试] chunk.__dict__: {pprint.pformat(chunk.__dict__)}")
                if hasattr(chunk, "choices"):
                    logger.info(f"[调试] chunk.choices: {pprint.pformat(chunk.choices)}")
                if hasattr(chunk, "delta"):
                    logger.info(f"[调试] chunk.delta: {pprint.pformat(chunk.delta)}")
                # 自动适配chunk结构
                delta = None
                if hasattr(chunk, "content") and chunk.content:
                    delta = chunk.content
                elif hasattr(chunk, "choices") and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, "delta") and hasattr(choice.delta, "content") and choice.delta.content:
                        delta = choice.delta.content
                elif hasattr(chunk, "delta") and hasattr(chunk.delta, "content") and chunk.delta.content:
                    delta = chunk.delta.content
                if delta:
                    full_content += delta
                    logger.info(f"[推送前端] conversation_id={conversation_id}, token={delta}")
                    yield {
                        "event": "message",
                        "data": json.dumps({
                            "content": delta,
                            "conversation_id": conversation_id
                        })
                    }
            logger.info("[流程] LLM token流式推理完成")
            # 保存AI回复到对话历史
            messages.append({
                "role": "assistant",
                "content": full_content
            })
            new_state = ChatState(messages=messages)
            await app_graph.ainvoke(new_state, config)
            yield {
                "event": "complete",
                "data": json.dumps({
                    "conversation_id": conversation_id
                })
            }
        except Exception as e:
            logger.error(f"[异常] /chat/stream 处理失败: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": str(e)
                })
            }
    return EventSourceResponse(generate_stream())

@app.post("/chat/stream")
async def chat_stream_post(request: Request):
    body = await request.json()
    message = body.get("message")
    conversation_id = body.get("conversation_id", "default")
    logger.info(f"[API] /chat/stream (POST) 收到请求，conversation_id={conversation_id}")

    async def generate_stream():
        try:
            config = {"configurable": {"thread_id": conversation_id}}
            current_state = await app_graph.aget_state(config)
            messages = current_state.values.get("messages", [])
            messages.append({
                "role": "user",
                "content": message
            })
            logger.info("[流程] 开始LLM token流式推理 (POST)")
            full_content = ""
            async for chunk in llm.astream(messages):
                delta = None
                if hasattr(chunk, "content") and chunk.content:
                    delta = chunk.content
                elif hasattr(chunk, "choices") and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, "delta") and hasattr(choice.delta, "content") and choice.delta.content:
                        delta = choice.delta.content
                elif hasattr(chunk, "delta") and hasattr(chunk.delta, "content") and chunk.delta.content:
                    delta = chunk.delta.content
                if delta:
                    full_content += delta
                    yield delta  # 直接返回文本 chunk，前端 fetch+流可直接拼接
            # 保存AI回复到对话历史
            messages.append({
                "role": "assistant",
                "content": full_content
            })
            new_state = ChatState(messages=messages)
            await app_graph.ainvoke(new_state, config)
        except Exception as e:
            logger.error(f"[异常] /chat/stream (POST) 处理失败: {e}")
            yield "[ERROR] " + str(e)
    from starlette.responses import StreamingResponse
    return StreamingResponse(generate_stream(), media_type="text/plain")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    logger.info(f"[API] /conversations/{conversation_id} 获取对话历史")
    try:
        config = {"configurable": {"thread_id": conversation_id}}
        state = await app_graph.aget_state(config)
        return {"messages": state.values.get("messages", [])}
    except Exception as e:
        logger.error(f"[异常] 获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    logger.info(f"[API] /conversations/{conversation_id} 删除对话")
    try:
        config = {"configurable": {"thread_id": conversation_id}}
        await app_graph.adelete(config)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"[异常] 删除对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/status")
async def get_config_status():
    logger.info("[API] /config/status 获取配置状态")
    try:
        config_status = get_llm_config()
        azure_endpoint = config_status["endpoint"]
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment_name = config_status["deployment"]
        
        config_status["status"] = "configured" if all([azure_endpoint, azure_api_key, deployment_name]) else "incomplete"
        return config_status
    except Exception as e:
        logger.error(f"[异常] 获取配置状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("[启动] 启动FastAPI服务...")
    print("=== main.py POST 路由测试 ===")
    uvicorn.run(app, host="0.0.0.0", port=8000) 