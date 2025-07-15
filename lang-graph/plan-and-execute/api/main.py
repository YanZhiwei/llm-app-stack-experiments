import json
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models import AgentResponse, GoalRequest

# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executor import Executor
from graph import AgentState, build_graph
from llm import LLM
from prompts import execute_prompt

app = FastAPI(title="Plan-and-Execute API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Plan-and-Execute 智能体 API"}

@app.post("/plan-and-execute", response_model=AgentResponse)
async def plan_and_execute(request: GoalRequest):
    try:
        # 构建并运行智能体
        g = build_graph()
        state = AgentState(goal=request.goal)
        final_state = g.invoke(state)
        
        # 返回结果
        return AgentResponse(
            goal=request.goal,
            plan=final_state["plan"],
            results=final_state["results"],
            history=final_state["history"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能体执行失败: {str(e)}")

@app.post("/plan-and-execute/stream")
async def plan_and_execute_stream(request: GoalRequest):
    """
    流式返回每一步执行建议，直接输出前端需要的格式。
    """
    try:
        from llm import LLM
        from plan import Plan
        from prompts import execute_prompt
        llm = LLM()
        
        def event_stream():
            try:
                steps = Plan(request.goal).generate_llm_steps()
                
                # 发送计划步骤信息
                plan_info = json.dumps({
                    "type": "plan",
                    "content": f"📋 共{len(steps)}个步骤，开始执行...\n\n"
                }, ensure_ascii=False)
                yield plan_info + "\n"
                
                for idx, step in enumerate(steps, 1):
                    # 发送步骤开始信息
                    step_start = json.dumps({
                        "type": "step_start", 
                        "content": f"**步骤 {idx}:** {step}\n\n"
                    }, ensure_ascii=False)
                    yield step_start + "\n"
                    
                    try:
                        for chunk in llm.stream(execute_prompt(step)):
                            content = getattr(chunk, "content", None)
                            if content and content.strip():
                                # 直接发送前端需要的格式
                                result_json = json.dumps({
                                    "type": "text",
                                    "content": content
                                }, ensure_ascii=False)
                                yield result_json + "\n"
                    except Exception as e:
                        # 发送错误信息
                        error_json = json.dumps({
                            "type": "error",
                            "content": f"❌ 步骤 {idx} 执行出错: {str(e)}\n\n"
                        }, ensure_ascii=False)
                        yield error_json + "\n"
                        continue  # 继续执行下一个步骤，而不是break
                    
                    # 发送步骤完成信息
                    step_end = json.dumps({
                        "type": "step_end",
                        "content": "\n---\n\n"
                    }, ensure_ascii=False)
                    yield step_end + "\n"
                
                # 发送完成信息
                complete_info = json.dumps({
                    "type": "complete",
                    "content": "✅ 所有步骤执行完成！"
                }, ensure_ascii=False)
                yield complete_info + "\n"
                
            except Exception as e:
                # 发送最终错误信息
                error_json = json.dumps({
                    "type": "error", 
                    "content": f"❌ 处理出错: {str(e)}"
                }, ensure_ascii=False)
                yield error_json + "\n"
        
        return StreamingResponse(event_stream(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式执行失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
