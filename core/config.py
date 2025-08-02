# core/config.py
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # RAG settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

settings = Settings()


