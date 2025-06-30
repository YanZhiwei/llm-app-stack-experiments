import logging

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from card import create_agent_card
from executor import HelloWorldAgentExecutor


@click.command()
@click.option("--host", default="localhost", help="Host to bind the server")
@click.option("--port", default=9999, help="Port to bind the server")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def main(host: str, port: int, reload: bool):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Hello World A2A Agent on {host}:{port}")

    agent_card = create_agent_card(host, port)
    agent_executor = HelloWorldAgentExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore())
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler)

    logger.info(f"服务启动中: http://{host}:{port}/")
    uvicorn.run(a2a_app.build(), host=host, port=port,
                reload=reload, log_level="info")


if __name__ == "__main__":
    main()
