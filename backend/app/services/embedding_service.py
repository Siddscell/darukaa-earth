from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import settings

class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
        return cls._instance
        
    async def initialize(self):
        if self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self.model.encode(texts)
