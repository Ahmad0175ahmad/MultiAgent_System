"""
Coder Agent — Generates, explains, reviews, and debugs code using LLMRouter.
"""

from typing import Any, Dict, List
import logging

from core.state import AgentState
from core.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CoderAgent:
    """
    CoderAgent handles all code-related tasks including:
    - Code generation
    - Code explanation
    - Code review
    - Debugging

    It routes requests to code-specialized LLMs via LLMRouter.
    """

    def __init__(self) -> None:
        """Initialize the CoderAgent with LLMRouter."""
        self.llm = LLMRouter()

    def run(self, state: AgentState) -> AgentState:
        """
        Execute coding task based on current task description.

        Args:
            state (AgentState): Shared system state

        Returns:
            AgentState: Updated state with coding results
        """
        try:
            task_id = state["current_task_id"]
            task_item = next(
                (t for t in state["tasks"] if t["id"] == task_id), None
            )

            if not task_item:
                raise ValueError(f"Task with id {task_id} not found")

            task_description: str = task_item.get("description", "")
            logger.info(f"CoderAgent processing task: {task_description}")

            # Step 1: Extract coding task
            coding_task = task_description

            # Step 2: Detect task type
            task_type = self._detect_task_type(coding_task)

            # Step 3: Build prompt
            prompt = self._build_prompt(task_type, coding_task, task_item)

            # Step 4: Call LLM
            response = self.llm.generate(
                prompt=prompt,
                task_type="code"
            )

            # Step 5: Parse output
            parsed_output = self._parse_output(response, task_type)

            # Step 8: Update state
            state["results"][task_id] = parsed_output

            return state

        except Exception as e:
            logger.error(f"CoderAgent error: {str(e)}")
            state["error_log"].append(f"CoderAgent: {str(e)}")
            return state

    def _detect_task_type(self, task: str) -> str:
        """
        Detect the type of coding task.

        Args:
            task (str): Task description

        Returns:
            str: Task type (generate | explain | review | debug)
        """
        task_lower = task.lower()

        if "explain" in task_lower:
            return "explain"
        elif "review" in task_lower or "improve" in task_lower:
            return "review"
        elif "debug" in task_lower or "fix" in task_lower or "error" in task_lower:
            return "debug"
        else:
            return "generate"

    def _build_prompt(
        self,
        task_type: str,
        task: str,
        task_item: Dict[str, Any]
    ) -> str:
        """
        Build specialized prompt based on task type.

        Args:
            task_type (str): Type of task
            task (str): Task description
            task_item (dict): Full task object

        Returns:
            str: Prompt for LLM
        """
        if task_type == "generate":
            return (
                f"Write clean Python code for: {task}. "
                "Include docstrings and type hints."
            )

        elif task_type == "explain":
            code = task_item.get("code", task)
            return f"Explain this code step by step:\n{code}"

        elif task_type == "review":
            code = task_item.get("code", task)
            return f"Review this code for bugs and improvements:\n{code}"

        elif task_type == "debug":
            code = task_item.get("code", "")
            error = task_item.get("error", "Unknown error")
            return f"Fix the bug in this code:\n{code}\nError: {error}"

        return task  # fallback

    def _parse_output(self, response: str, task_type: str) -> Dict[str, Any]:
        """
        Parse LLM output into structured format.

        Args:
            response (str): Raw LLM output
            task_type (str): Task type

        Returns:
            dict: Structured output
        """
        try:
            return {
                "code": response if task_type in ["generate", "debug"] else "",
                "language": "python",
                "explanation": response if task_type in ["explain", "review"] else "",
                "requirements": self._extract_requirements(response),
                "task_type": task_type,
            }

        except Exception as e:
            logger.error(f"Parsing error: {str(e)}")
            return {
                "code": "",
                "language": "python",
                "explanation": "Failed to parse response",
                "requirements": [],
                "task_type": task_type,
            }

    def _extract_requirements(self, text: str) -> List[str]:
        """
        Extract possible requirements or dependencies from text.

        Args:
            text (str): LLM output

        Returns:
            List[str]: List of requirements
        """
        requirements = []

        try:
            lines = text.split("\n")
            for line in lines:
                if "import " in line:
                    parts = line.replace("import", "").strip().split()
                    if parts:
                        requirements.append(parts[0])

        except Exception as e:
            logger.warning(f"Requirement extraction failed: {str(e)}")

        return list(set(requirements))