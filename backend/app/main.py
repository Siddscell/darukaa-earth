from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.routers import health, chat, environment, recommendations, knowledge

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    # Initialize embedding service
    embedding_svc = EmbeddingService()
    await embedding_svc.initialize()
    # Initialize vector store
    vs = VectorStoreService()
    if vs.get_collection_count() == 0:
        from scripts.ingest_knowledge import ingest_seed_data
        ingest_seed_data()
    yield
    # shutdown
    pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered environmental intelligence system",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
app.include_router(environment.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
