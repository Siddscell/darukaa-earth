"""
Recommendations router: direct recommendations from structured profile input.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.recommendation import RecommendationRequest
from app.schemas.chat import ChatResponse
from app.reasoning.reasoning_engine import generate_reasoning_chain
from app.reasoning.recommendation_engine import generate_recommendations, build_reasoning_trace
from app.rag.pipeline import RAGPipeline
from app.llm.provider import LLMProvider
from app.models.recommendation import Recommendation, EvidenceSource
from app.database import AsyncSessionLocal
from sqlalchemy import select
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

rag_pipeline = RAGPipeline()
llm_provider = LLMProvider()


@router.post("/recommendations")
async def get_recommendations(req: RecommendationRequest):
    """Generate recommendations directly from an environmental profile."""
    try:
        profile_dict = req.profile.model_dump(exclude_none=True)
        query = req.query or "What environmental interventions should I consider?"

        # Reasoning
        reasoning_result = generate_reasoning_chain(profile_dict)

        # RAG
        rag_result = rag_pipeline.run(
            query=query,
            env_profile=profile_dict,
            active_variables=reasoning_result.get("active_variables", []),
        )
        ranked_docs = rag_result.get("ranked_docs", [])

        # Generate
        recommendations, summary, is_demo = await generate_recommendations(
            profile=profile_dict,
            reasoning_result=reasoning_result,
            ranked_docs=ranked_docs,
            user_query=query,
            llm_provider=llm_provider,
        )

        reasoning_trace = build_reasoning_trace(
            profile_dict, reasoning_result, ranked_docs, []
        )

        return {
            "summary": summary,
            "recommendations": [r.model_dump() for r in recommendations],
            "reasoning_trace": reasoning_trace.model_dump(),
            "demo_mode": is_demo,
            "evidence_count": len(ranked_docs),
        }

    except Exception as e:
        logger.error(f"Recommendations error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evidence/{recommendation_id}")
async def get_evidence(recommendation_id: str):
    """Return evidence sources for a saved recommendation."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(EvidenceSource).where(
                EvidenceSource.recommendation_id == recommendation_id
            )
        )
        sources = result.scalars().all()
        if not sources:
            raise HTTPException(
                status_code=404,
                detail="No evidence found for this recommendation ID."
            )
        return {
            "recommendation_id": recommendation_id,
            "evidence": [
                {
                    "id": s.id,
                    "title": s.title,
                    "source": s.source_org,
                    "year": s.year,
                    "url": s.url,
                    "topic": s.topic,
                    "variables": s.variables_json,
                    "evidence_type": s.evidence_type,
                    "supporting_excerpt": s.supporting_excerpt,
                }
                for s in sources
            ],
        }
