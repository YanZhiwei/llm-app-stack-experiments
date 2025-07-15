from dataclasses import dataclass, field
from typing import List

from langgraph.graph import END, StateGraph

from executor import Executor
from memory import Memory
from plan import Plan


@dataclass
class AgentState:
    goal: str
    plan: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

# 节点函数
def plan_node(state: AgentState):
    print(f"[Plan阶段] 用户目标: {state.goal}")
    steps = Plan(state.goal).generate_llm_steps()
    print(f"[Plan阶段] 解析后的步骤:")
    for idx, step in enumerate(steps, 1):
        print(f"  {idx}. {step}")
    state.plan = steps
    return state

def execute_node(state: AgentState):
    print(f"[Execute阶段] 共 {len(state.plan)} 步骤")
    results = Executor().execute_steps(state.plan)
    for idx, result in enumerate(results, 1):
        print(f"[Execute阶段] LLM建议({idx}):\n{result}\n")
    state.results = results
    return state

def memory_node(state: AgentState):
    memory = Memory()
    for r in state.results:
        memory.add(r)
    state.history = memory.get_all()
    return state

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("plan", plan_node)
    g.add_node("execute", execute_node)
    g.add_node("memory", memory_node)
    g.add_edge("plan", "execute")
    g.add_edge("execute", "memory")
    g.add_edge("memory", END)
    g.set_entry_point("plan")
    return g.compile() 