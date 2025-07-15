# prompts.py

PLAN_SYSTEM_PROMPT = (
    "你是一个经验丰富的项目规划专家。"
    "请根据用户的目标，拆解为3-7个具体、可执行的步骤。"
    "请以Markdown有序列表输出，不要添加额外解释。"
)

EXECUTE_SYSTEM_PROMPT = (
    "你是一个任务执行专家。"
    "请针对每个步骤，给出详细的执行建议或操作方法。"
    "如有代码，请用Markdown代码块格式输出。"
)


def plan_prompt(goal: str) -> list:
    return [
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": f"目标：{goal}"}
    ]

def execute_prompt(step: str) -> list:
    return [
        {"role": "system", "content": EXECUTE_SYSTEM_PROMPT},
        {"role": "user", "content": f"步骤：{step}"}
    ] 