import asyncio


class HelloWorldAgent:
    """Hello World 代理核心逻辑"""

    def __init__(self):
        self.name = "HelloWorldAgent"
        self.version = "1.0.0"

    async def invoke(self) -> str:
        return "Hello World from A2A Agent! 🤖"

    async def stream(self):
        chunks = ["Hello ", "World ", "from ", "A2A ", "Agent! ", "🚀"]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.1)

    async def process_message(self, message: str) -> str:
        if not message.strip():
            return "Please provide a message to process."
        if "hello" in message.lower():
            return f"Hello there! You said: '{message}'"
        elif "help" in message.lower():
            return (
                "I'm a simple A2A agent. I can:\n"
                "- Say hello\n"
                "- Echo your messages\n"
                "- Provide basic responses\n"
                "Try saying 'hello' or ask me anything!"
            )
        else:
            return f"Thanks for your message: '{message}'. I'm a simple echo agent! 🔄"
