from llm import LLM
from prompts import execute_prompt


class Executor:
    def __init__(self):
        self.llm = LLM()

    def execute_steps(self, steps):
        results = []
        for step in steps:
            result = self.llm.chat(execute_prompt(step))
            results.append(result)
        return results

    def execute_steps_stream(self, steps):
        for step in steps:
            # 返回 step 和 LLM 的流式生成器
            yield step, self.llm.stream(execute_prompt(step))
