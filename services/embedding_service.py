# services/embedding_service.py
import logging
from sentence_transformers import SentenceTransformer
from core.config import settings

logger = logging.getLogger(__name__)

class GlobalEmbeddingService:
    """Singleton service for managing the SentenceTransformer model globally"""
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalEmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the SentenceTransformer model once"""
        try:
            logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("SentenceTransformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise
    
    def encode(self, texts):
        """Encode texts using the global model"""
        if self._model is None:
            self._load_model()
        return self._model.encode(texts)
    
    @property
    def model(self):
        """Get the model instance"""
        if self._model is None:
            self._load_model()
        return self._model

# Global instance
global_embedding_service = GlobalEmbeddingService()
