# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

# 定义 FastAPI 应用
app = FastAPI()


def create_frontend_router(build_dir="frontend/dist"):
    """创建用于提供 React 前端的路由器。

    参数:
        build_dir: 相对于项目根目录的 React 构建目录路径。

    返回:
        提供前端的 Starlette 应用程序。
    """
    # 获取项目根目录（从后端向上两级）
    project_root = pathlib.Path(__file__).parent.parent.parent.parent
    build_path = project_root / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"警告: 在 {build_path} 未找到前端构建目录或不完整。提供前端可能会失败。"
        )
        # 如果构建未准备好，返回虚拟路由器
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "前端未构建。在前端目录中运行 'npm run build'。",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# 将前端挂载到 /app 下以避免与 LangGraph API 路由冲突
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
