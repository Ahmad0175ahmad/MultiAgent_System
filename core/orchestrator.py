# """
# LangGraph Orchestrator (M8 — Wired Agents)

# Flow:
# START → decompose_goal → route_tasks → [researcher_node | writer_node] → route_tasks (loop) → synthesize → END
# """

# from typing import Dict, Any, Optional, Callable
# import logging
# import json
# import uuid
# import re

# from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.memory import MemorySaver

# from core.state import AgentState
# from core.llm_router import LLMRouter
# from core.memory import MemoryManager

# # ✅ NEW: import agents
# from agents.researcher import ResearcherAgent
# from agents.writer import WriterAgent


# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


# class OrchestratorGraph:
#     SUPPORTED_AGENT_TYPES = {"researcher", "writer"}
#     MAX_TASKS = 3

#     def __init__(
#         self,
#         config: Optional[Dict[str, Any]] = None,
#         status_callback: Optional[Callable[[str, int], None]] = None,
#     ):
#         self.config = config or {}
#         self.status_callback = status_callback
#         self.llm = LLMRouter(
#             preferred_provider=self.config.get("llm_provider") or self.config.get("provider"),
#             preferred_model=self.config.get("llm_model") or self.config.get("model"),
#         )
#         self.memory = MemoryManager()

#         # ✅ NEW: init agents
#         self.researcher = ResearcherAgent(llm=self.llm)
#         self.writer = WriterAgent(llm=self.llm)

#         self.builder = StateGraph(AgentState)

#         # Nodes
#         self.builder.add_node("decompose_goal", self.decompose_goal)
#         self.builder.add_node("route_tasks", self.route_tasks)
#         self.builder.add_node("researcher_node", self.researcher_node)
#         self.builder.add_node("writer_node", self.writer_node)
#         self.builder.add_node("synthesize", self.synthesize)

#         # Entry
#         self.builder.set_entry_point("decompose_goal")

#         # Static edges
#         self.builder.add_edge("decompose_goal", "route_tasks")

#         # ✅ CONDITIONAL ROUTING
#         self.builder.add_conditional_edges(
#             "route_tasks",
#             self._route_decision,
#             {
#                 "researcher": "researcher_node",
#                 "writer": "writer_node",
#                 "synthesize": "synthesize",
#             },
#         )

#         # Loop back
#         self.builder.add_edge("researcher_node", "route_tasks")
#         self.builder.add_edge("writer_node", "route_tasks")

#         self.builder.add_edge("synthesize", END)

#         self.checkpointer = MemorySaver()
#         self.graph = self.builder.compile(checkpointer=self.checkpointer)

#     def _update_status(self, agent: str, step: int) -> None:
#         if self.status_callback:
#             self.status_callback(agent, step)

#     # -----------------------------------
#     # ROUTE DECISION FUNCTION
#     # -----------------------------------
#     def _route_decision(self, state: AgentState) -> str:
#         """
#         Decide next step:
#         - researcher / writer / synthesize
#         """
#         tasks = state.get("tasks", [])

#         # If all done → synthesize
#         if all(t.get("status") == "completed" for t in tasks):
#             return "synthesize"

#         current_task = self._get_current_task(state)
#         if not current_task:
#             return "synthesize"

#         agent_type = str(current_task.get("agent_type", "writer")).lower()
#         if agent_type not in self.SUPPORTED_AGENT_TYPES:
#             logger.warning(
#                 "Unsupported agent_type '%s' for task %s, falling back to writer",
#                 agent_type,
#                 current_task.get("task_id") or current_task.get("id"),
#             )
#             return "writer"

#         return agent_type

#         return "synthesize"

#     def _get_next_pending_task(self, state: AgentState) -> Optional[Dict[str, Any]]:
#         """Return the next executable task, skipping completed or failed entries."""
#         for task in state.get("tasks", []):
#             if task.get("status") not in ["completed", "failed"]:
#                 return task
#         return None

#     def _get_current_task(self, state: AgentState) -> Optional[Dict[str, Any]]:
#         current_task_id = str(state.get("current_task_id", ""))
#         if not current_task_id:
#             return None

#         for task in state.get("tasks", []):
#             task_id = str(task.get("task_id") or task.get("id") or "")
#             if task_id == current_task_id:
#                 return task
#         return None

#     # -----------------------------------
#     # NODE 1: DECOMPOSE GOAL
#     # -----------------------------------
#     def decompose_goal(self, state: AgentState) -> AgentState:
#         try:
#             self._update_status("decompose_goal", 1)
#             logger.info("Decomposing goal into tasks")

#             prompt = f"""
#             Break this goal into at most 2 structured tasks.

#             Goal:
#             {state['goal']}

#             Return JSON list with agent_types strictly from:
#             researcher, writer

#             Return ONLY valid JSON. Do not add markdown fences or explanation text.

#             Format:
#             [
#             {{
#                 "task_id": "1",
#                 "description": "...",
#                 "agent_type": "researcher",
#                 "depends_on": [],
#                 "status": "pending"
#             }}
#             ]
#             """

#             response = self.llm.chat(
#                 prompt,
#                 speed_priority=True,
#                 timeout=float(self.config.get("decompose_timeout", 20)),
#                 num_predict=180,
#                 response_format="json",
#             )

#             try:
#                 tasks = self._parse_tasks_response(response)
#             except Exception:
#                 logger.warning("Invalid JSON, fallback task")
#                 tasks = self._fallback_tasks(state["goal"])

#             normalized_tasks = self._sanitize_tasks(tasks, state["goal"])
#             state["tasks"] = normalized_tasks
#             return state

#         except Exception as e:
#             logger.error(f"Decompose failed: {e}")
#             state["error_log"].append(str(e))
#             state["tasks"] = self._sanitize_tasks(self._fallback_tasks(state["goal"]), state["goal"])
#             return state

#     def _parse_tasks_response(self, response: str) -> list[Dict[str, Any]]:
#         """Parse plain JSON or JSON embedded in markdown fences/text."""
#         try:
#             parsed = json.loads(response)
#             if isinstance(parsed, list):
#                 return parsed
#         except Exception:
#             pass

#         match = re.search(r"(\[\s*\{.*\}\s*\])", response, re.DOTALL)
#         if match:
#             parsed = json.loads(match.group(1))
#             if isinstance(parsed, list):
#                 return parsed

#         raise ValueError("Could not parse tasks JSON response")

#     def _fallback_tasks(self, goal: str) -> list[Dict[str, Any]]:
#         """Return a deterministic task plan when LLM decomposition is slow or fails."""
#         goal_lower = goal.lower()
#         research_keywords = ("research", "compare", "analysis", "analyze", "search", "find")

#         if any(keyword in goal_lower for keyword in research_keywords):
#             return [
#                 {
#                     "task_id": "1",
#                     "description": goal,
#                     "agent_type": "researcher",
#                     "depends_on": [],
#                     "status": "pending",
#                 },
#                 {
#                     "task_id": "2",
#                     "description": f"Write the final response for: {goal}",
#                     "agent_type": "writer",
#                     "depends_on": ["1"],
#                     "status": "pending",
#                     "format": self.config.get("output_format", "report"),
#                 },
#             ]

#         return [{
#             "task_id": "1",
#             "description": goal,
#             "agent_type": "writer",
#             "depends_on": [],
#             "status": "pending",
#             "format": self.config.get("output_format", "report"),
#         }]

#     def _sanitize_tasks(self, tasks: list[Dict[str, Any]], goal: str) -> list[Dict[str, Any]]:
#         """
#         Normalize LLM-generated tasks into a short plan that only uses supported agents.
#         """
#         sanitized: list[Dict[str, Any]] = []
#         seen_signatures: set[tuple[str, str]] = set()

#         for raw_task in tasks:
#             normalized = self._normalize_task(raw_task)
#             agent_type = str(normalized.get("agent_type", "writer")).lower()

#             if agent_type not in self.SUPPORTED_AGENT_TYPES:
#                 description = str(normalized.get("description", "")).lower()
#                 if "research" in description or "search" in description or "find" in description:
#                     agent_type = "researcher"
#                 else:
#                     agent_type = "writer"
#                 normalized["agent_type"] = agent_type

#             signature = (
#                 normalized["agent_type"],
#                 str(normalized.get("description", "")).strip().lower(),
#             )
#             if signature in seen_signatures:
#                 continue
#             seen_signatures.add(signature)
#             sanitized.append(normalized)

#         if not sanitized:
#             sanitized = [self._normalize_task(task) for task in self._fallback_tasks(goal)]

#         has_research = any(task.get("agent_type") == "researcher" for task in sanitized)
#         has_writer = any(task.get("agent_type") == "writer" for task in sanitized)

#         compact_plan: list[Dict[str, Any]] = []

#         if has_research:
#             first_research = next(task for task in sanitized if task.get("agent_type") == "researcher")
#             first_research["task_id"] = "1"
#             first_research["id"] = "1"
#             first_research["depends_on"] = []
#             compact_plan.append(first_research)

#         writer_task = next((task for task in sanitized if task.get("agent_type") == "writer"), None)
#         if not writer_task:
#             writer_task = self._normalize_task({
#                 "task_id": "2" if has_research else "1",
#                 "description": f"Write the final response for: {goal}",
#                 "agent_type": "writer",
#                 "depends_on": ["1"] if has_research else [],
#                 "status": "pending",
#                 "format": self.config.get("output_format", "report"),
#             })

#         writer_task["task_id"] = "2" if has_research else "1"
#         writer_task["id"] = writer_task["task_id"]
#         writer_task["depends_on"] = ["1"] if has_research else []
#         writer_task["format"] = writer_task.get("format", self.config.get("output_format", "report"))
#         compact_plan.append(writer_task)

#         return compact_plan[: self.MAX_TASKS]

#     def _normalize_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
#         normalized = dict(task)

#         if "task_id" not in normalized and "id" in normalized:
#             normalized["task_id"] = normalized["id"]

#         if "id" not in normalized and "task_id" in normalized:
#             normalized["id"] = normalized["task_id"]

#         if "status" not in normalized:
#             normalized["status"] = "pending"

#         if "agent_type" not in normalized:
#             normalized["agent_type"] = "writer"

#         if normalized["agent_type"] == "writer" and "format" not in normalized:
#             normalized["format"] = self.config.get("output_format", "report")

#         # Normalize identifiers to strings
#         if "task_id" in normalized:
#             normalized["task_id"] = str(normalized["task_id"])
#         if "id" in normalized:
#             normalized["id"] = str(normalized["id"])

#         if "task_id" not in normalized and "id" in normalized:
#             normalized["task_id"] = normalized["id"]
#         if "id" not in normalized and "task_id" in normalized:
#             normalized["id"] = normalized["task_id"]

#         return normalized

#     # -----------------------------------
#     # NODE 2: ROUTE TASKS (lightweight)
#     # -----------------------------------
#     def route_tasks(self, state: AgentState) -> AgentState:
#         """
#         Select and persist the next task before conditional routing runs.
#         """
#         self._update_status("route_tasks", 2)
#         next_task = self._get_next_pending_task(state)

#         if next_task:
#             current_task_id = str(next_task.get("task_id") or next_task.get("id") or "")
#             state["current_task_id"] = current_task_id
#             logger.info(
#                 "Routing decision node selected task %s (%s)",
#                 current_task_id,
#                 next_task.get("agent_type", "writer"),
#             )
#         else:
#             state["current_task_id"] = ""
#             logger.info("Routing decision node found no pending tasks")

#         return state

#     # -----------------------------------
#     # NODE: RESEARCHER
#     # -----------------------------------
#     def researcher_node(self, state: AgentState) -> AgentState:
#         try:
#             self._update_status("researcher_node", 3)
#             logger.info("Executing ResearcherAgent")

#             state = self.researcher.run(state)

#             # mark task complete
#             if self._current_task_has_result(state):
#                 self._mark_current_task_done(state)
#             else:
#                 self._mark_current_task_status(state, "failed")

#             return state

#         except Exception as e:
#             logger.error(f"Researcher failed: {e}")
#             state["error_log"].append(str(e))
#             self._mark_current_task_status(state, "failed")
#             return state

#     # -----------------------------------
#     # NODE: WRITER
#     # -----------------------------------
#     def writer_node(self, state: AgentState) -> AgentState:
#         try:
#             self._update_status("writer_node", 3)
#             logger.info("Executing WriterAgent")

#             state = self.writer.run(state)

#             # mark task complete
#             if self._current_task_has_result(state):
#                 self._mark_current_task_done(state)
#             else:
#                 self._mark_current_task_status(state, "failed")

#             return state

#         except Exception as e:
#             logger.error(f"Writer failed: {e}")
#             state["error_log"].append(str(e))
#             self._mark_current_task_status(state, "failed")
#             return state

#     # -----------------------------------
#     # HELPER
#     # -----------------------------------
#     def _mark_current_task_done(self, state: AgentState):
#         self._mark_current_task_status(state, "completed")

#     def _current_task_has_result(self, state: AgentState) -> bool:
#         tid = str(state.get("current_task_id", ""))
#         if not tid:
#             return False

#         return tid in state.get("results", {}) or bool(state.get("final_output"))

#     def _mark_current_task_status(self, state: AgentState, status: str):
#         tid = state.get("current_task_id")
#         for t in state["tasks"]:
#             if str(t.get("task_id", "")) == str(tid) or str(t.get("id", "")) == str(tid):
#                 t["status"] = status
#                 break

#     # -----------------------------------
#     # NODE: SYNTHESIZE
#     # -----------------------------------
#     def synthesize(self, state: AgentState) -> AgentState:
#         try:
#             self._update_status("synthesize", 4)
#             logger.info("Synthesizing final output")

#             if state.get("final_output", "").strip():
#                 logger.info("Final output already prepared by writer; preserving formatted result")
#                 return state

#             state["final_output"] = self.writer.synthesize_all(state)
#             return state

#         except Exception as e:
#             logger.error(f"Synthesis failed: {e}")
#             state["error_log"].append(str(e))
#             return state

#     # -----------------------------------
#     # RUN GRAPH
#     # -----------------------------------
#     def run(self, goal: str, config: dict = None, session_id: str = None) -> AgentState:
#         try:
#             session_id = session_id or str(uuid.uuid4())

#             initial_state: AgentState = {
#                 "goal": goal,
#                 "tasks": [],
#                 "current_task_id": "",
#                 "results": {},
#                 "memory_context": [],
#                 "final_output": "",
#                 "error_log": [],
#                 "session_id": session_id,
#             }

#             logger.info(f"Starting graph: {session_id}")

#             # ✅ Graph handles looping internally
#             final_state = self.graph.invoke(
#                 initial_state,
#                 config={"configurable": {"thread_id": session_id}}
#             )

#             return final_state

#         except Exception as e:
#             logger.error(f"Execution failed: {e}")
#             raise


# # -----------------------------------
# # TEST
# # -----------------------------------
# if __name__ == "__main__":
#     orchestrator = OrchestratorGraph()

#     result = orchestrator.run(
#         "Research Python web frameworks and write a comparison"
#     )

#     print("\n=== FINAL OUTPUT ===")
#     print(result["final_output"])


"""
LangGraph Orchestrator — All 5 Agents Wired
Flow: START → decompose_goal → route_tasks → [agent] → route_tasks (loop) → synthesize → END
"""

from typing import Dict, Any, Optional, Callable
import logging
import json
import uuid
import re

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import AgentState
from core.llm_router import LLMRouter
from core.memory import MemoryManager

# ✅ All 5 agents
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from agents.critic import CriticAgent
from agents.coder import CoderAgent
from agents.rag_agent import RAGAgent


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OrchestratorGraph:

    # ✅ All 5 agent types supported
    SUPPORTED_AGENT_TYPES = {"researcher", "writer", "critic", "coder", "rag"}
    MAX_TASKS = 5

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        status_callback: Optional[Callable[[str, int], None]] = None,
    ):
        self.config = config or {}
        self.status_callback = status_callback

        self.llm = LLMRouter(
            preferred_provider=self.config.get("llm_provider") or self.config.get("provider"),
            preferred_model=self.config.get("llm_model") or self.config.get("model"),
        )
        self.memory = MemoryManager()

        # ✅ Init all 5 agents
        self.researcher = ResearcherAgent(llm=self.llm)
        self.writer     = WriterAgent(llm=self.llm)
        self.critic     = CriticAgent()
        self.coder      = CoderAgent()
        self.rag        = RAGAgent()

        # ── Build Graph ───────────────────────────────────────────────────────
        self.builder = StateGraph(AgentState)

        # Nodes
        self.builder.add_node("decompose_goal",  self.decompose_goal)
        self.builder.add_node("route_tasks",     self.route_tasks)
        self.builder.add_node("researcher_node", self.researcher_node)
        self.builder.add_node("writer_node",     self.writer_node)
        self.builder.add_node("critic_node",     self.critic_node)
        self.builder.add_node("coder_node",      self.coder_node)
        self.builder.add_node("rag_node",        self.rag_node)
        self.builder.add_node("synthesize",      self.synthesize)

        # Entry
        self.builder.set_entry_point("decompose_goal")

        # Static edges
        self.builder.add_edge("decompose_goal", "route_tasks")

        # ✅ Conditional routing — all 5 agents
        self.builder.add_conditional_edges(
            "route_tasks",
            self._route_decision,
            {
                "researcher": "researcher_node",
                "writer":     "writer_node",
                "critic":     "critic_node",
                "coder":      "coder_node",
                "rag":        "rag_node",
                "synthesize": "synthesize",
            },
        )

        # All agents loop back to route_tasks
        self.builder.add_edge("researcher_node", "route_tasks")
        self.builder.add_edge("writer_node",     "route_tasks")
        self.builder.add_edge("critic_node",     "route_tasks")
        self.builder.add_edge("coder_node",      "route_tasks")
        self.builder.add_edge("rag_node",        "route_tasks")

        self.builder.add_edge("synthesize", END)

        self.checkpointer = MemorySaver()
        self.graph = self.builder.compile(checkpointer=self.checkpointer)

    # ─── Status Helper ────────────────────────────────────────────────────────
    def _update_status(self, agent: str, step: int) -> None:
        if self.status_callback:
            self.status_callback(agent, step)

    # ─── Routing Logic ────────────────────────────────────────────────────────
    def _route_decision(self, state: AgentState) -> str:
        tasks = state.get("tasks", [])

        if all(t.get("status") == "completed" for t in tasks):
            return "synthesize"

        current_task = self._get_current_task(state)
        if not current_task:
            return "synthesize"

        agent_type = str(current_task.get("agent_type", "writer")).lower()

        if agent_type not in self.SUPPORTED_AGENT_TYPES:
            logger.warning("Unknown agent_type '%s', falling back to writer", agent_type)
            return "writer"

        return agent_type

    def _get_next_pending_task(self, state: AgentState) -> Optional[Dict[str, Any]]:
        for task in state.get("tasks", []):
            if task.get("status") not in ["completed", "failed"]:
                return task
        return None

    def _get_current_task(self, state: AgentState) -> Optional[Dict[str, Any]]:
        current_task_id = str(state.get("current_task_id", ""))
        if not current_task_id:
            return None
        for task in state.get("tasks", []):
            task_id = str(task.get("task_id") or task.get("id") or "")
            if task_id == current_task_id:
                return task
        return None

    # ─── Node 1: Decompose Goal ───────────────────────────────────────────────
    def decompose_goal(self, state: AgentState) -> AgentState:
        try:
            self._update_status("decompose_goal", 1)
            logger.info("Decomposing goal into tasks")

            prompt = f"""
            Break this goal into at most 3 structured tasks.

            Goal:
            {state['goal']}

            Available agent_types:
            - researcher  → web search, finding facts
            - writer      → writing reports, summaries, structured output
            - critic      → reviewing and improving written output
            - coder       → generating, explaining, reviewing Python code
            - rag         → answering questions from uploaded documents

            Rules:
            - Use "coder" ONLY if the goal explicitly asks for code
            - Use "rag" ONLY if the goal mentions "document", "uploaded file", or "PDF"
            - Always end with "writer" to produce final output
            - Use "critic" after writer if quality review is needed

            Return ONLY valid JSON list. No markdown, no explanation.

            Format:
            [
            {{
                "task_id": "1",
                "description": "...",
                "agent_type": "researcher",
                "depends_on": [],
                "status": "pending"
            }}
            ]
            """

            response = self.llm.chat(
                prompt,
                speed_priority=True,
                timeout=float(self.config.get("decompose_timeout", 20)),
                num_predict=300,
                response_format="json",
            )

            try:
                tasks = self._parse_tasks_response(response)
            except Exception:
                logger.warning("Invalid JSON from LLM, using fallback tasks")
                tasks = self._fallback_tasks(state["goal"])

            normalized_tasks = self._sanitize_tasks(tasks, state["goal"])
            state["tasks"] = normalized_tasks
            logger.info("Tasks created: %s", [f"{t['task_id']}:{t['agent_type']}" for t in normalized_tasks])
            return state

        except Exception as e:
            logger.error(f"Decompose failed: {e}")
            state["error_log"].append(str(e))
            state["tasks"] = self._sanitize_tasks(self._fallback_tasks(state["goal"]), state["goal"])
            return state

    def _parse_tasks_response(self, response: str) -> list:
        try:
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        match = re.search(r"(\[\s*\{.*\}\s*\])", response, re.DOTALL)
        if match:
            parsed = json.loads(match.group(1))
            if isinstance(parsed, list):
                return parsed

        raise ValueError("Could not parse tasks JSON")

    def _fallback_tasks(self, goal: str) -> list:
        goal_lower = goal.lower()

        # Code task
        if any(k in goal_lower for k in ("code", "script", "function", "program", "write a python")):
            return [
                {"task_id": "1", "description": goal, "agent_type": "coder", "depends_on": [], "status": "pending"},
            ]

        # Document/RAG task
        if any(k in goal_lower for k in ("document", "pdf", "uploaded", "file")):
            return [
                {"task_id": "1", "description": goal, "agent_type": "rag", "depends_on": [], "status": "pending"},
            ]

        # Research + write (default)
        if any(k in goal_lower for k in ("research", "compare", "analysis", "find", "search")):
            return [
                {"task_id": "1", "description": goal, "agent_type": "researcher", "depends_on": [], "status": "pending"},
                {"task_id": "2", "description": f"Write final response for: {goal}", "agent_type": "writer", "depends_on": ["1"], "status": "pending", "format": self.config.get("output_format", "report")},
            ]

        # Default: just write
        return [
            {"task_id": "1", "description": goal, "agent_type": "writer", "depends_on": [], "status": "pending", "format": self.config.get("output_format", "report")},
        ]

    def _sanitize_tasks(self, tasks: list, goal: str) -> list:
        sanitized = []
        seen: set = set()

        for raw in tasks:
            t = self._normalize_task(raw)
            agent_type = str(t.get("agent_type", "writer")).lower()

            if agent_type not in self.SUPPORTED_AGENT_TYPES:
                agent_type = "writer"
                t["agent_type"] = agent_type

            sig = (agent_type, str(t.get("description", "")).strip().lower())
            if sig in seen:
                continue
            seen.add(sig)
            sanitized.append(t)

        if not sanitized:
            sanitized = [self._normalize_task(t) for t in self._fallback_tasks(goal)]

        # Re-index task IDs sequentially
        for i, t in enumerate(sanitized, start=1):
            t["task_id"] = str(i)
            t["id"]      = str(i)

        return sanitized[: self.MAX_TASKS]

    def _normalize_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        t = dict(task)
        if "task_id" not in t and "id" in t:
            t["task_id"] = t["id"]
        if "id" not in t and "task_id" in t:
            t["id"] = t["task_id"]
        if "status" not in t:
            t["status"] = "pending"
        if "agent_type" not in t:
            t["agent_type"] = "writer"
        if t["agent_type"] == "writer" and "format" not in t:
            t["format"] = self.config.get("output_format", "report")
        if "task_id" in t:
            t["task_id"] = str(t["task_id"])
        if "id" in t:
            t["id"] = str(t["id"])
        return t

    # ─── Node 2: Route Tasks ──────────────────────────────────────────────────
    def route_tasks(self, state: AgentState) -> AgentState:
        self._update_status("route_tasks", 2)
        next_task = self._get_next_pending_task(state)

        if next_task:
            tid = str(next_task.get("task_id") or next_task.get("id") or "")
            state["current_task_id"] = tid
            logger.info("Next task: %s (%s)", tid, next_task.get("agent_type"))
        else:
            state["current_task_id"] = ""
            logger.info("No pending tasks — moving to synthesize")

        return state

    # ─── Node: Researcher ─────────────────────────────────────────────────────
    def researcher_node(self, state: AgentState) -> AgentState:
        try:
            self._update_status("researcher_node", 3)
            logger.info("Running ResearcherAgent")
            state = self.researcher.run(state)
            self._mark_task(state, "completed" if self._has_result(state) else "failed")
        except Exception as e:
            logger.error(f"Researcher error: {e}")
            state["error_log"].append(str(e))
            self._mark_task(state, "failed")
        return state

    # ─── Node: Writer ─────────────────────────────────────────────────────────
    def writer_node(self, state: AgentState) -> AgentState:
        try:
            self._update_status("writer_node", 3)
            logger.info("Running WriterAgent")
            state = self.writer.run(state)
            self._mark_task(state, "completed" if self._has_result(state) else "failed")
        except Exception as e:
            logger.error(f"Writer error: {e}")
            state["error_log"].append(str(e))
            self._mark_task(state, "failed")
        return state

    # ─── Node: Critic ─────────────────────────────────────────────────────────
    def critic_node(self, state: AgentState) -> AgentState:
        try:
            self._update_status("critic_node", 3)
            logger.info("Running CriticAgent")
            state = self.critic.run(state)
            self._mark_task(state, "completed" if self._has_result(state) else "failed")
        except Exception as e:
            logger.error(f"Critic error: {e}")
            state["error_log"].append(str(e))
            self._mark_task(state, "failed")
        return state

    # ─── Node: Coder ──────────────────────────────────────────────────────────
    def coder_node(self, state: AgentState) -> AgentState:
        try:
            self._update_status("coder_node", 3)
            logger.info("Running CoderAgent")
            state = self.coder.run(state)
            self._mark_task(state, "completed" if self._has_result(state) else "failed")
        except Exception as e:
            logger.error(f"Coder error: {e}")
            state["error_log"].append(str(e))
            self._mark_task(state, "failed")
        return state

    # ─── Node: RAG ────────────────────────────────────────────────────────────
    def rag_node(self, state: AgentState) -> AgentState:
        try:
            self._update_status("rag_node", 3)
            logger.info("Running RAGAgent")
            state = self.rag.run(state)
            self._mark_task(state, "completed" if self._has_result(state) else "failed")
        except Exception as e:
            logger.error(f"RAG error: {e}")
            state["error_log"].append(str(e))
            self._mark_task(state, "failed")
        return state

    # ─── Node: Synthesize ─────────────────────────────────────────────────────
    def synthesize(self, state: AgentState) -> AgentState:
        try:
            self._update_status("synthesize", 4)
            logger.info("Synthesizing final output")

            if state.get("final_output", "").strip():
                logger.info("Writer already produced final output — skipping synthesis")
                return state

            state["final_output"] = self.writer.synthesize_all(state)
            return state

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            state["error_log"].append(str(e))
            return state

    # ─── Helpers ──────────────────────────────────────────────────────────────
    def _has_result(self, state: AgentState) -> bool:
        tid = str(state.get("current_task_id", ""))
        if not tid:
            return False
        return tid in state.get("results", {}) or bool(state.get("final_output"))

    def _mark_task(self, state: AgentState, status: str):
        tid = str(state.get("current_task_id", ""))
        for t in state.get("tasks", []):
            if str(t.get("task_id", "")) == tid or str(t.get("id", "")) == tid:
                t["status"] = status
                break

    # ─── Run ──────────────────────────────────────────────────────────────────
    def run(self, goal: str, config: dict = None, session_id: str = None) -> AgentState:
        session_id = session_id or str(uuid.uuid4())

        initial_state: AgentState = {
            "goal":             goal,
            "tasks":            [],
            "current_task_id":  "",
            "results":          {},
            "memory_context":   [],
            "final_output":     "",
            "error_log":        [],
            "session_id":       session_id,
        }

        logger.info("Starting session: %s", session_id)

        final_state = self.graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}}
        )

        return final_state


# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    orchestrator = OrchestratorGraph()

    result = orchestrator.run("Research Python web frameworks and write a comparison report")

    print("\n=== FINAL OUTPUT ===")
    print(result["final_output"])

    print("\n=== TASKS EXECUTED ===")
    for t in result["tasks"]:
        print(f"  {t['task_id']} | {t['agent_type']} | {t['status']}")
