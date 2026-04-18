"""
Writer/Synthesizer Agent (Module M7)

Responsible for:
- Combining outputs from previous agents
- Generating structured final responses using LLM
- Storing final outputs in memory
"""

from typing import Any, Dict, List
from datetime import datetime
import logging

from core.state import AgentState
from core.memory import MemoryManager
from core.llm_router import LLMRouter
from config import settings


logger = logging.getLogger(__name__)


class WriterAgent:
    """
    Writer Agent:
    - Synthesizes research + intermediate outputs
    - Produces final structured content
    """

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.memory = MemoryManager()
        self.llm = llm or LLMRouter()
        self.llm_timeout = 45.0

    def _get_current_task(self, state: AgentState) -> Dict[str, Any]:
        """Fetch current task from state."""
        current_task_id = str(state.get("current_task_id", ""))
        for task in state.get("tasks", []):
            if str(task.get("id", "")) == current_task_id or str(task.get("task_id", "")) == current_task_id:
                return task
        return {}

    def _format_results(self, results: Dict[str, Any]) -> str:
        """Convert results dict into readable text for prompt."""
        formatted_chunks: List[str] = []

        for task_id, data in results.items():
            chunk = f"### Task {task_id}\n"

            if isinstance(data, dict):
                summary = data.get("summary", "")
                key_facts = data.get("key_facts", [])
                sources = data.get("sources", [])

                if summary:
                    chunk += f"Summary:\n{summary}\n\n"

                if key_facts:
                    chunk += "Key Facts:\n"
                    for fact in key_facts:
                        chunk += f"- {fact}\n"

                if sources:
                    chunk += "\nSources:\n"
                    for s in sources:
                        chunk += f"- {s.get('title')} ({s.get('url')})\n"

            else:
                chunk += str(data)

            formatted_chunks.append(chunk)

        return "\n\n".join(formatted_chunks)

    def _build_writing_prompt(self, goal: str, results_text: str, fmt: str) -> tuple[str, str]:
        """Create a consistent markdown-first writing prompt."""
        system_prompt = (
            f"You are a professional technical writer. Write in {fmt} format.\n"
            "Return clean markdown with clear sections, readable bullets, and fenced code blocks for code.\n"
            "Do not dump raw dictionaries or JSON. Keep the explanation well-structured, practical, and moderately detailed."
        )
        user_prompt = (
            f"Goal:\n{goal}\n\n"
            f"Research data:\n{results_text}\n\n"
            "Requirements:\n"
            "- Start with a short title.\n"
            "- Explain the theory in a clear sequence.\n"
            "- If code is relevant, include one or two Python examples in ```python fenced blocks.\n"
            "- Keep the response practical, but detailed enough to be useful for learning.\n"
            "- End with a concise takeaway."
        )
        return system_prompt, user_prompt

    def _validate_format(self, text: str, fmt: str) -> bool:
        """Basic validation for output format."""
        if not text:
            return False

        if fmt == "bullets":
            return "-" in text or "*" in text
        elif fmt == "report":
            return "#" in text or "##" in text
        elif fmt == "comparison":
            return "|" in text or "vs" in text.lower()
        elif fmt == "summary":
            return len(text.split()) > 20

        return True

    def synthesize_all(self, state: AgentState) -> str:
        """
        Combine all results into one coherent output.
        Used as final synthesis step.
        """
        try:
            goal = state.get("goal", "")
            results_text = self._format_results(state.get("results", {}))

            prompt = (
                "You are a professional writer.\n"
                "Create a clear, cohesive final answer in markdown.\n"
                "Use headings, concise bullets where helpful, and fenced code blocks for code.\n"
                "Do not output raw dictionaries.\n\n"
                f"Goal:\n{goal}\n\n"
                f"All Data:\n{results_text}\n\n"
                "Write a polished final response."
            )

            response = self.llm.generate(
                prompt,
                max_tokens=2048,
                speed_priority=True,
                timeout=self.llm_timeout,
            )
            return str(response)

        except Exception as e:
            logger.exception("synthesize_all failed")
            return self._fallback_text(goal, results_text)

    def run(self, state: AgentState) -> AgentState:
        """
        Execute writer workflow.

        Steps:
        1. Collect results
        2. Determine format
        3. Build prompt
        4. Generate output via LLM
        5. Validate format
        6. Store output
        7. Update state
        """
        try:
            task = self._get_current_task(state)
            task_id = state.get("current_task_id")

            if not task:
                raise ValueError("Current task not found")

            goal = state.get("goal", "")
            fmt = task.get("format", "report")

            # ---------------------------
            # 1. Collect results
            # ---------------------------
            results_text = self._format_results(state.get("results", {}))

            # ---------------------------
            # 2. Build prompt
            # ---------------------------
            system_prompt, user_prompt = self._build_writing_prompt(goal, results_text, fmt)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # ---------------------------
            # 3. LLM call
            # ---------------------------
            try:
                generated_text = str(
                    self.llm.generate(
                        full_prompt,
                        max_tokens=2048,
                        speed_priority=True,
                        timeout=self.llm_timeout,
                        num_predict=420,
                    )
                )
            except Exception:
                logger.exception("Primary writer generation failed, using fallback formatter")
                generated_text = self._fallback_text(goal, results_text, fmt)

            # ---------------------------
            # 4. Validate format
            # ---------------------------
            if not self._validate_format(generated_text, fmt):
                logger.warning("Output format validation failed, retrying with stricter prompt")

                retry_prompt = (
                    f"{system_prompt}\n"
                    "STRICTLY follow the requested format. Return markdown only, with fenced code blocks.\n\n"
                    f"{user_prompt}"
                )

                try:
                    generated_text = str(
                        self.llm.generate(
                            retry_prompt,
                            max_tokens=2048,
                            speed_priority=True,
                            timeout=self.llm_timeout,
                            num_predict=420,
                        )
                    )
                except Exception:
                    logger.exception("Retry generation failed, keeping fallback output")
                    generated_text = self._fallback_text(goal, results_text, fmt)

            # ---------------------------
            # 5. Store in memory
            # ---------------------------
            timestamp = datetime.utcnow().isoformat()
            self.memory.store(
                collection_name="task_outputs",
                text=generated_text,
                metadata={
                    "task_id": task_id,
                    "timestamp": timestamp,
                    "format": fmt,
                    "goal": goal,
                },
                doc_id=f"writer_{task_id}_{timestamp}"
            )

            # ---------------------------
            # 6. Update state
            # ---------------------------
            state["results"][task_id] = {
                "summary": generated_text,
                "format": fmt,
                "goal": goal,
            }
            state["final_output"] = generated_text

            return state

        except Exception as e:
            logger.exception("WriterAgent failed")

            state.setdefault("error_log", []).append(str(e))
            return state

    def _fallback_text(self, goal: str, results_text: str, fmt: str = "report") -> str:
        """Generate deterministic output when all LLM calls fail."""
        if fmt == "bullets":
            return f"- Goal: {goal}\n- Available context:\n{results_text or 'No prior context available.'}"
        if fmt == "summary":
            return f"## Summary\n\nGoal: {goal}\n\n{results_text or 'No prior context available.'}"
        if fmt == "comparison":
            return f"## Comparison\n\nGoal: {goal}\n\n{results_text or 'No comparison context available.'}"
        return f"# Final Report\n\n## Goal\n{goal}\n\n## Collected Context\n{results_text or 'No prior context available.'}"
