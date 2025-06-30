from a2a.types import AgentCapabilities, AgentCard, AgentSkill


def create_agent_card(host: str = "localhost", port: int = 9999) -> AgentCard:
    """创建代理卡片，描述代理的能力和元数据"""
    hello_skill = AgentSkill(
        id="hello_world",
        name="Hello World",
        description="A simple greeting skill that says hello and echoes messages",
        tags=["greeting", "echo", "basic"],
        examples=["hello", "hi there", "what can you do?"]
    )
    agent_card = AgentCard(
        name="Hello World A2A Agent",
        description="A simple A2A agent that demonstrates basic greeting and echo functionality",
        url=f"http://{host}:{port}",
        version="1.0.0",
        skills=[hello_skill],
        capabilities=AgentCapabilities(),
        defaultInputModes=["text"],
        defaultOutputModes=["text"]
    )
    return agent_card
