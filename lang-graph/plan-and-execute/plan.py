from llm import LLM
from prompts import plan_prompt


class Plan:
    def __init__(self, goal: str):
        self.goal = goal

    def generate_llm_steps(self):
        llm = LLM()
        plan_text = llm.chat(plan_prompt(self.goal))
        steps = [s.strip() for s in plan_text.split("\n") if s.strip()]
        return steps
