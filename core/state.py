"""
Agent State Definition (M5)

Shared state across all agents in LangGraph.
"""

from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    """
    Global shared state for AutoAgent system.
    """

    goal: str
    tasks: List[dict]  # {task_id, description, agent_type, depends_on, status}
    current_task_id: str
    results: Dict[str, Any]
    memory_context: List[str]
    final_output: str
    error_log: List[str]
    session_id: str