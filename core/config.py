# core/config.py

import os
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
logger.debug(f"Environment variables loaded. OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}, MONGODB_URL: {os.getenv('MONGODB_URL')}")

class Settings:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "callcenter_rag")
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", "./vector_db")
    
    # RAG settings
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

settings = Settings()
logger.debug(f"Settings initialized: DATABASE_NAME={settings.DATABASE_NAME}, MONGODB_URL={settings.MONGODB_URL}")

