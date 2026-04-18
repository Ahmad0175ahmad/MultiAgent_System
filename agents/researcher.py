"""
Researcher Agent (Module M6)

Responsible for:
- Performing web search
- Extracting key facts using LLM
- Caching results in ChromaDB
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
import json
import logging

from core.state import AgentState
from core.memory import MemoryManager
from core.tools import get_search_tool
from core.llm_router import LLMRouter
from config import settings


logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher Agent:
    - Searches web using tools
    - Extracts structured insights via LLM
    - Caches results in ChromaDB
    """

    def __init__(self, llm: LLMRouter | None = None) -> None:
        self.memory = MemoryManager()
        self.search_tool = get_search_tool()
        self.llm = llm or LLMRouter()
        self.llm_timeout = 45.0

    def _is_recent(self, timestamp: str) -> bool:
        """Check if cached result is within last 24 hours."""
        try:
            ts = datetime.fromisoformat(timestamp)
            return datetime.utcnow() - ts < timedelta(hours=24)
        except Exception:
            return False

    def _get_current_task(self, state: AgentState) -> Dict[str, Any]:
        """Fetch current task from state."""
        current_task_id = str(state.get("current_task_id", ""))
        for task in state.get("tasks", []):
            if str(task.get("id", "")) == current_task_id or str(task.get("task_id", "")) == current_task_id:
                return task
        return {}

    def _compact_search_results(self, search_results: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, str]]]:
        """Trim search results so provider prompts stay focused and cheap."""
        snippets: List[str] = []
        sources: List[Dict[str, str]] = []

        for result in search_results[:3]:
            snippet = (result.get("snippet") or "").strip()
            if snippet:
                snippets.append(snippet[:500])
            sources.append({
                "title": result.get("title"),
                "url": result.get("url"),
            })

        return snippets, sources

    def run(self, state: AgentState) -> AgentState:
        """
        Execute researcher workflow.

        Steps:
        1. Extract query/topic
        2. Check cache
        3. Perform search if needed
        4. Extract facts via LLM
        5. Store in memory
        6. Update state
        """
        try:
            task = self._get_current_task(state)
            task_id = state.get("current_task_id")

            if not task:
                raise ValueError("Current task not found in state")

            search_query: str = task.get("search_query") or task.get("description")
            topic: str = task.get("topic") or search_query

            # ---------------------------
            # 1. Check cache
            # ---------------------------
            cached_docs = self.memory.retrieve(
                collection_name="research_memory",
                query=topic,
                k=1
            )

            if cached_docs:
                doc = cached_docs[0]
                metadata = doc.get("metadata", {})
                timestamp = metadata.get("timestamp")

                if timestamp and self._is_recent(timestamp):
                    logger.info(f"Using cached research for topic: {topic}")

                    output = doc.get("data", {})
                    output["cached"] = True

                    state["results"][task_id] = output
                    return state

            # ---------------------------
            # 2. Perform search
            # ---------------------------
            logger.info(f"Performing web search for: {search_query}")

            search_results = self.search_tool.search(search_query)
            snippets, sources = self._compact_search_results(search_results)

            # ---------------------------
            # 3. LLM extraction
            # ---------------------------
            prompt = (
                "Extract up to 5 key facts and one short summary.\n\n"
                f"Search Results:\n{snippets}\n\n"
                "Return:\n"
                "- Key Facts (bullet points)\n"
                "- Summary (short paragraph, 4 sentences max)"
            )

            llm_response = self.llm.generate(
                prompt,
                speed_priority=True,
                timeout=self.llm_timeout,
                num_predict=220,
            )

            # Basic parsing (robust fallback)
            key_facts: List[str] = []
            summary: str = ""

            if isinstance(llm_response, dict):
                key_facts = llm_response.get("key_facts", [])
                summary = llm_response.get("summary", "")
            else:
                # fallback parsing
                text = str(llm_response)
                lines = text.split("\n")
                key_facts = [
                    l.lstrip("-* ").strip()
                    for l in lines
                    if l.strip().startswith(("-", "*"))
                ]
                summary = text

            # ---------------------------
            # 4. Build output
            # ---------------------------
            timestamp = datetime.utcnow().isoformat()

            output: Dict[str, Any] = {
                "sources": sources,
                "key_facts": key_facts,
                "summary": summary,
                "cached": False,
                "timestamp": timestamp,
            }

            # ---------------------------
            # 5. Store in memory
            # ---------------------------
            self.memory.store(
                collection_name="research_memory",
                text=summary,
                metadata={
                    "topic": topic,
                    "timestamp": timestamp,
                    "source_urls": json.dumps([s["url"] for s in sources]),
                    "summary": summary,
                },
                doc_id=f"research_{task_id}_{timestamp}",
            )

            # ---------------------------
            # 6. Update state
            # ---------------------------
            state["results"][task_id] = output

            return state

        except Exception as e:
            logger.exception("ResearcherAgent failed")

            state.setdefault("error_log", []).append(str(e))
            return state
