class ToolManager:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def call(self, name, *args, **kwargs):
        if name in self.tools:
            return self.tools[name](*args, **kwargs)
        raise ValueError(f"工具 {name} 未注册")

