"""
Health and system status endpoints.
"""
import logging
from fastapi import APIRouter
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.vector_store import VectorStoreService
from app.services.embedding_service import EmbeddingService
from app.llm.provider import LLMProvider
from sqlalchemy import text

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple liveness check."""
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/api/system/status")
async def system_status():
    """Detailed component health report."""
    status = {
        "database": False,
        "vector_db": False,
        "embeddings": False,
        "ollama_available": False,
        "ollama_model": None,
        "knowledge_base_docs": 0,
        "demo_mode": True,
    }

    # Database check
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        status["database"] = True
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")

    # Vector DB check
    try:
        vs = VectorStoreService()
        count = vs.get_collection_count()
        status["vector_db"] = True
        status["knowledge_base_docs"] = count
    except Exception as e:
        logger.warning(f"Vector DB health check failed: {e}")

    # Embeddings check
    try:
        emb = EmbeddingService()
        if emb.model is not None:
            status["embeddings"] = True
        else:
            # Try to load
            emb.embed_texts(["test"])
            status["embeddings"] = True
    except Exception as e:
        logger.warning(f"Embeddings health check failed: {e}")

    # LLM provider check
    try:
        provider = LLMProvider()
        available = await provider.is_available()
        status["ollama_available"] = available
        status["demo_mode"] = not available
        if available:
            status["ollama_model"] = settings.OLLAMA_MODEL
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")

    return status
