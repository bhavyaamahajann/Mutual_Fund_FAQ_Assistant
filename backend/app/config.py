"""
Mutual Fund FAQ Assistant — Application Configuration

Loads environment variables from .env and exposes them as typed settings
via Pydantic BaseSettings. All configurable values are centralised here.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Path constants (relative to project root)
# ---------------------------------------------------------------------------
# Project root is two levels up from this file:
#   backend/app/config.py  →  project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = PROJECT_ROOT / "backend"
DATA_DIR = BACKEND_DIR / "data"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
CORPUS_URLS_PATH = DATA_DIR / "corpus_urls.json"
FUND_METADATA_PATH = DATA_DIR / "fund_metadata.json"


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Groq ----
    groq_api_key: str = ""

    # ---- Model configuration ----
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_model: str = "llama-3.3-70b-versatile"


    # ---- RAG configuration ----
    top_k: int = 3
    chunk_size: int = 500
    chunk_overlap: int = 50

    # ---- ChromaDB ----
    chroma_collection_name: str = "mutual_fund_faq"

    # ---- Server ----
    host: str = "0.0.0.0"
    port: int = 8000

    # ---- Paths (derived, not from env) ----
    @property
    def chroma_db_path(self) -> Path:
        return CHROMA_DB_DIR

    @property
    def corpus_urls_path(self) -> Path:
        return CORPUS_URLS_PATH

    @property
    def fund_metadata_path(self) -> Path:
        return FUND_METADATA_PATH


# ---------------------------------------------------------------------------
# Singleton instance — import this everywhere
# ---------------------------------------------------------------------------
settings = Settings()


# ---------------------------------------------------------------------------
# Ensure required data directories exist
# ---------------------------------------------------------------------------
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
