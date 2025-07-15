from typing import List

from pydantic import BaseModel


class GoalRequest(BaseModel):
    goal: str

class AgentResponse(BaseModel):
    goal: str
    plan: List[str]
    results: List[str]
    history: List[str]
