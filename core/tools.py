"""
Search Tools Module (M4)

Provides:
- Tavily search (primary)
- DuckDuckGo search (fallback)
- Search router
- LangGraph tool wrapper

Author: AutoAgent
"""

from typing import List, Dict
import logging
import json

from config import settings

# Tavily
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

# DuckDuckGo
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# LangGraph tool decorator
try:
    from langchain.tools import tool
except ImportError:
    tool = None


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# -----------------------------------
# TAVILY SEARCH TOOL
# -----------------------------------
class TavilySearchTool:
    """
    Tavily-based web search tool
    """

    def __init__(self):
        if not getattr(settings, "TAVILY_API_KEY", None):
            raise ValueError(
                "TAVILY_API_KEY is missing. Please set it in .env/config.py"
            )

        if TavilyClient is None:
            raise ImportError("tavily-python package not installed")

        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform Tavily search

        Returns:
            List[Dict[{title, url, snippet}]]
        """
        try:
            logger.info("Using Tavily search")

            response = self.client.search(
                query=query,
                max_results=max_results
            )

            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "snippet": item.get("content"),
                })

            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []


# -----------------------------------
# DUCKDUCKGO SEARCH TOOL
# -----------------------------------
class DuckDuckGoSearchTool:
    """
    DuckDuckGo-based search tool (fallback)
    """

    def __init__(self):
        if DDGS is None:
            raise ImportError("duckduckgo-search package not installed")

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform DuckDuckGo search

        Returns:
            List[Dict[{title, url, snippet}]]
        """
        try:
            logger.info("Using DuckDuckGo search")

            results = []

            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title"),
                        "url": r.get("href"),
                        "snippet": r.get("body"),
                    })

            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []


# -----------------------------------
# SEARCH ROUTER
# -----------------------------------
def get_search_tool():
    """
    Returns the appropriate search tool:
    - Tavily if API key exists
    - Otherwise DuckDuckGo
    """
    try:
        if getattr(settings, "TAVILY_API_KEY", None):
            logger.info("SearchRouter → Tavily selected")
            return TavilySearchTool()

        logger.info("SearchRouter → DuckDuckGo selected")
        return DuckDuckGoSearchTool()

    except Exception as e:
        logger.error(f"SearchRouter failed: {e}")
        raise


# -----------------------------------
# LANGGRAPH TOOL WRAPPER
# -----------------------------------
if tool:

    @tool
    def tavily_search_tool(query: str) -> str:
        """
        LangGraph-compatible Tavily search tool.
        Returns JSON string of results.
        """
        try:
            search_tool = get_search_tool()
            results = search_tool.search(query)

            return json.dumps(results, indent=2)

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return json.dumps({"error": str(e)})

else:
    def tavily_search_tool(query: str) -> str:
        """Fallback if LangChain tool decorator not available"""
        try:
            search_tool = get_search_tool()
            results = search_tool.search(query)

            return json.dumps(results, indent=2)

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return json.dumps({"error": str(e)})