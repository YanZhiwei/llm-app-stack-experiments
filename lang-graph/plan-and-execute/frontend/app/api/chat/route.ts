export const runtime = "edge";
export const maxDuration = 30;

interface MessageContent {
  type: string;
  text?: string;
}

interface Message {
  role: string;
  content: string | MessageContent[];
}

interface ErrorWithCode extends Error {
  code?: string;
}

// 全局错误处理函数
const handleError = (error: unknown, context: string): void => {
  const err = error as ErrorWithCode;
  // 忽略正常的中断和连接错误
  if (err.name === 'AbortError' || 
      err.code === 'ECONNRESET' ||
      err.code === 'ERR_INVALID_STATE' ||
      err.message.includes('aborted') ||
      err.message.includes('Controller is already closed') ||
      err.message.includes('This operation was aborted')) {
    return;
  }
  console.error(`${context}:`, error);
};

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const messages = Array.isArray(body.messages) ? body.messages : [];
    const userMessage = [...messages].reverse().find((m: Message) => m.role === "user");
    let goal = "";
    
    if (userMessage?.content) {
      if (typeof userMessage.content === "string") {
        goal = userMessage.content.trim();
      } else if (Array.isArray(userMessage.content)) {
        const textPart = userMessage.content.find((c: MessageContent) => c.type === "text" && typeof c.text === "string");
        if (textPart && textPart.text) {
          goal = textPart.text.trim();
        }
      }
    }

    if (!goal) {
      return new Response(JSON.stringify({ error: "No user goal provided", detail: { messages } }), { status: 400 });
    }

    // 调用 FastAPI 的流式接口
    let apiRes: Response;
    try {
      apiRes = await fetch("http://localhost:8000/plan-and-execute/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal }),
        // 禁用缓存以避免 AbortController 相关问题
        cache: 'no-store',
        // 不使用 AbortController 来避免缓存冲突
      });
    } catch (error) {
      handleError(error, "Fetch请求失败");
      return new Response(JSON.stringify({ error: "无法连接到后端API", detail: String(error) }), { status: 500 });
    }
    
    if (!apiRes.body) {
      const errText = await apiRes.text();
      return new Response(JSON.stringify({ error: "后端API无流响应", detail: errText }), { status: 500 });
    }

    // 直接转发后端的流式数据
    const encoder = new TextEncoder();
    const decoder = new TextDecoder("utf-8");
    
    const stream = new ReadableStream({
      async start(controller) {
        let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
        let buffer = "";
        let isControllerClosed = false;
        let cleanupDone = false;
        
        // 安全写入函数
        const safeEnqueue = (data: string): boolean => {
          if (isControllerClosed || cleanupDone) return false;
          
          try {
            controller.enqueue(encoder.encode(data));
            return true;
          } catch (error) {
            handleError(error, "写入数据失败");
            isControllerClosed = true;
            return false;
          }
        };
        
        // 安全关闭控制器
        const safeClose = (): void => {
          if (isControllerClosed || cleanupDone) return;
          
          try {
            controller.close();
            isControllerClosed = true;
          } catch (error) {
            handleError(error, "关闭控制器失败");
          }
        };
        
        // 清理函数
        const cleanup = (): void => {
          if (cleanupDone) return;
          cleanupDone = true;
          
          try {
            if (reader) {
              reader.releaseLock();
              reader = null;
            }
          } catch (error) {
            handleError(error, "释放读取器失败");
          }
          
          safeClose();
        };
        
        try {
          reader = apiRes.body!.getReader();
          
          while (!cleanupDone) {
            let result;
            try {
              result = await reader.read();
            } catch (error) {
              handleError(error, "读取流数据失败");
              break;
            }
            
            const { done, value } = result;
            if (done) break;
            
            try {
              buffer += decoder.decode(value, { stream: true });
            } catch (error) {
              handleError(error, "解码数据失败");
              break;
            }
            
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";
            
            for (const line of lines) {
              const trimmedLine = line.trim();
              if (trimmedLine === "" || isControllerClosed || cleanupDone) continue;
              
              try {
                // 验证JSON格式
                const data = JSON.parse(trimmedLine);
                const success = safeEnqueue(JSON.stringify(data) + "\n");
                if (!success) break;
              } catch (parseError) {
                handleError(parseError, `JSON解析失败: "${trimmedLine}"`);
                continue;
              }
            }
            
            if (isControllerClosed || cleanupDone) break;
          }
          
          // 处理最后剩余的 buffer
          if (buffer.trim() !== "" && !isControllerClosed && !cleanupDone) {
            try {
              const data = JSON.parse(buffer.trim());
              safeEnqueue(JSON.stringify(data) + "\n");
            } catch (parseError) {
              handleError(parseError, `Buffer JSON解析失败: "${buffer}"`);
            }
          }
        } catch (error) {
          handleError(error, "流处理错误");
        } finally {
          cleanup();
        }
      },
      cancel() {
        try {
          // 简化取消操作，避免 AbortController 相关问题
          if (apiRes.body) {
            const reader = apiRes.body.getReader();
            reader.cancel().catch((error) => {
              handleError(error, "取消读取器失败");
            });
          }
        } catch (error) {
          handleError(error, "取消操作失败");
        }
      }
    });
    
    return new Response(stream, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (e) {
    handleError(e, "API处理异常");
    return new Response(JSON.stringify({ error: "前端API处理异常", detail: String(e) }), { status: 500 });
  }
}
