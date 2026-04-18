"""
System health checks for AutoAgent.
"""

import logging
import httpx
from typing import Dict

from config import settings  # assumes config.py exposes settings
import chromadb

logger = logging.getLogger(__name__)
def check_chromadb() -> bool:
    """Check if ChromaDB is accessible."""
    try:
        client = chromadb.Client()
        client.list_collections()
        return True
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {e}")
        return False


def check_groq() -> bool:
    """Check Groq API availability."""
    if not settings.GROQ_API_KEY:
        logger.warning("Groq API key not set.")
        return False

    try:
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        response = httpx.get(
            "https://api.groq.com/openai/v1/models",
            headers=headers,
            timeout=5.0,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Groq health check failed: {e}")
        return False


def check_tavily() -> bool:
    """Check Tavily API availability."""
    if not settings.TAVILY_API_KEY:
        logger.warning("Tavily API key not set.")
        return False

    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={"query": "health check", "api_key": settings.TAVILY_API_KEY},
            timeout=5.0,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Tavily health check failed: {e}")
        return False


def get_full_health() -> Dict[str, bool]:
    """
    Run all health checks.

    Returns:
        Dict with service statuses
    """
    return {
        "chromadb": check_chromadb(),
        "groq": check_groq(),
        "gemini": bool(settings.GEMINI_API_KEY),
        "tavily": check_tavily(),
    }
