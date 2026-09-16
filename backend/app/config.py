from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Darukaa.Earth AI Biodiversity Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./darukaa.db"
    DATABASE_PATH: str = "./darukaa.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_EVIDENCE: str = "environmental_evidence"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_ENABLED: bool = True
    
    # RAG
    MAX_RETRIEVED_DOCS: int = 6
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    
    # API
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
