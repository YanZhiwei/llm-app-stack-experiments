import logging
from typing import Optional

from a2a.server.agent_execution import AgentExecutor
from a2a.types import DataPart, TextPart
from a2a.utils.message import new_agent_text_message

from core_agent import HelloWorldAgent

logger = logging.getLogger(__name__)


class HelloWorldAgentExecutor(AgentExecutor):
    """A2A 代理执行器，处理任务执行逻辑"""

    def __init__(self):
        self.agent = HelloWorldAgent()

    async def execute(self, context, event_queue) -> None:
        try:
            user_message = self._extract_user_message(context)
            if user_message:
                response = await self.agent.process_message(user_message)
            else:
                response = await self.agent.invoke()
            await event_queue.enqueue_event(new_agent_text_message(response))
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            await event_queue.enqueue_event(new_agent_text_message(error_message))

    async def cancel(self, context, event_queue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("Task has been cancelled."))

    def _extract_user_message(self, context) -> Optional[str]:
        try:
            if hasattr(context, 'message') and context.message:
                message = context.message
                if hasattr(message, 'parts') and message.parts:
                    for part in message.parts:
                        if isinstance(part, TextPart) and hasattr(part, 'text'):
                            return part.text.strip()
                        elif isinstance(part, DataPart) and hasattr(part, 'data'):
                            if isinstance(part.data, str):
                                return part.data.strip()
                            elif isinstance(part.data, dict) and 'text' in part.data:
                                return str(part.data['text']).strip()
        except Exception as e:
            logger.warning(f"Could not extract user message: {e}")
        return None
