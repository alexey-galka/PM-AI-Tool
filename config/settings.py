"""Application configuration"""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
MODELS_DIR = DATA_DIR / 'ai_models'
CHROMA_DIR = DATA_DIR / 'chroma_db'
AUDIO_STORAGE_DIR = DATA_DIR / 'audio_storage'
TRANSCRIPTS_DIR = DATA_DIR / 'transcripts'
DATABASE_PATH = DATA_DIR / 'pm_tool.db'


def ensure_dirs():
    """Creates necessary directories"""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


# Ollama settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lfm2.5:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL", "jeffh/intfloat-multilingual-e5-large:f16")

# Whisper settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_CACHE_DIR = MODELS_DIR / 'whisper'

# RAG settings
RAG_SEARCH_RESULTS = int(os.getenv("RAG_SEARCH_RESULTS", "10"))

# Application settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
APP_NAME = "PM AI Tool"
APP_VERSION = "1.0.0"
