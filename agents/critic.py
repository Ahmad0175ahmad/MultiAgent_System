"""
Critic Agent (Module M10)
Performs quality assurance on outputs and triggers revisions if needed.
"""

from typing import Any, Dict
import json
import logging

from core.state import AgentState
from core.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CriticAgent:
    """Quality Reviewer Agent"""

    def __init__(self):
        self.llm = LLMRouter()
        self.max_revisions = 2

    def run(self, state: AgentState) -> AgentState:
        """
        Review latest output and decide approval or revision.
        """
        try:
            # -----------------------------
            # Get latest output
            # -----------------------------
            output = state.get("final_output")

            if not output:
                # fallback: get latest task result
                results = state.get("results", {})
                if results:
                    last_key = list(results.keys())[-1]
                    output = results[last_key]
                else:
                    raise ValueError("No output found to review")

            # Ensure string format
            if isinstance(output, dict):
                output_text = json.dumps(output, indent=2)
            else:
                output_text = str(output)

            # -----------------------------
            # Build prompt
            # -----------------------------
            system_prompt = "You are a quality reviewer. Return ONLY valid JSON."
            user_prompt = (
                "Review this output for quality, accuracy, completeness:\n"
                f"{output_text}\n\n"
                "Return JSON: {score: 0-10, issues: [str], improved_output: str, approved: bool}"
            )

            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            # -----------------------------
            # Parse JSON
            # -----------------------------
            try:
                review = json.loads(response)
            except json.JSONDecodeError:
                logger.warning("LLM returned invalid JSON, attempting fix")
                response_fixed = response.strip().split("```")[-1]
                review = json.loads(response_fixed)

            score = review.get("score", 0)
            issues = review.get("issues", [])
            improved_output = review.get("improved_output", output_text)
            approved = review.get("approved", False)

            # -----------------------------
            # Track revision count
            # -----------------------------
            results = state.setdefault("results", {})
            revision_count = results.get("_critic_revisions", 0)

            # -----------------------------
            # Decision logic
            # -----------------------------
            if (not approved and score < 7) and revision_count < self.max_revisions:
                # Add issues to error log
                state.setdefault("error_log", []).extend(issues)

                # Increment revision count
                revision_count += 1
                results["_critic_revisions"] = revision_count

                # Flag for revision (orchestrator should route to Writer)
                state["needs_revision"] = True

                logger.info(f"Critic rejected output. Revision {revision_count}")
                return state

            # Approve or max revisions reached
            state["final_output"] = improved_output
            state["needs_revision"] = False

            logger.info("Critic approved output")
            return state

        except Exception as e:
            logger.exception("Error in CriticAgent.run")
            state.setdefault("error_log", []).append(str(e))
            return state
