from fastapi import APIRouter

router = APIRouter()

@router.post("/knowledge/ingest")
def ingest_knowledge():
    return {"status": "ingested"}

@router.get("/knowledge/stats")
def knowledge_stats():
    return {"docs_count": 25}
