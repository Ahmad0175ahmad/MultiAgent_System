"""
Application configuration module.

Loads environment variables using python-dotenv and validates them
using Pydantic BaseSettings.

Usage:
    from config import settings
"""

#from pydantic import BaseSettings, Field
# Yeh nai line lagao
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Load environment variables from the project-local .env file
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """
    Central configuration class for AutoAgent system.
    All values are loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
        extra="ignore",
    )

    # =========================
    # LLM CONFIGURATION
    # =========================

    GROQ_API_KEY: str = Field(
        ..., description="API key for Groq LLM service"
    )

    GEMINI_API_KEY: str = Field(
        ..., description="API key for Google Gemini"
    )

    DEFAULT_LLM_PROVIDER: str = Field(
        default="groq", description="Default LLM provider (groq/gemini)"
    )

    DEFAULT_LLM_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Default model name for the selected provider"
    )

    GROQ_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model ID for chat completions"
    )

    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model ID for content generation"
    )

    # =========================
    # EXTERNAL TOOLS
    # =========================

    TAVILY_API_KEY: str = Field(
        ..., description="API key for Tavily search tool"
    )

    # =========================
    # STORAGE PATHS
    # =========================

    CHROMADB_PATH: str = Field(
        ..., description="Path to ChromaDB persistent storage"
    )

    UPLOADS_PATH: str = Field(
        ..., description="Directory for uploaded documents"
    )

    SESSIONS_DB_PATH: str = Field(
        ..., description="SQLite database path for session storage"
    )

    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )

    EMBEDDING_LOCAL_FILES_ONLY: bool = Field(
        default=True,
        description="Load embedding model from local cache only when available"
    )

    # =========================
    # FASTAPI SERVER CONFIG
    # =========================

    FASTAPI_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for FastAPI server"
    )

    FASTAPI_PORT: int = Field(
        default=8000,
        description="Port for FastAPI server"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, value):
        """Accept common non-boolean environment values without crashing startup."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", ""}:
                return False
        return value

# Singleton instance for global use
settings = Settings()
