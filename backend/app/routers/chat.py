"""
Chat router — the core conversational endpoint.
"""
import uuid
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, ReasoningTrace
from app.memory.conversation_memory import ConversationMemory
from app.reasoning.environmental_extractor import extract_environmental_profile, detect_user_intent
from app.reasoning.missing_info_detector import get_missing_info, needs_clarification
from app.reasoning.reasoning_engine import generate_reasoning_chain
from app.reasoning.recommendation_engine import generate_recommendations, build_reasoning_trace
from app.rag.pipeline import RAGPipeline
from app.llm.provider import LLMProvider
from app.llm.fallback import generate_clarification_message, DEMO_MODE_NOTICE

logger = logging.getLogger(__name__)
router = APIRouter()

memory = ConversationMemory()
rag_pipeline = RAGPipeline()
llm_provider = LLMProvider()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Main conversational endpoint."""
    try:
        # 1. Get or create conversation
        conversation_id = req.conversation_id
        if not conversation_id or not await memory.conversation_exists(conversation_id):
            conversation_id = await memory.create_conversation(
                session_id=req.session_id or str(uuid.uuid4()),
                title=req.message[:60],
            )

        # 2. Add user message
        await memory.add_message(conversation_id, "user", req.message)

        # 3. Get existing context
        context = await memory.get_conversation_context(conversation_id)
        existing_profile = context.get("environmental_profile", {})

        # 4. Extract new environmental data from this message
        extracted = extract_environmental_profile(req.message)

        # 5. Merge into stored profile
        merged_profile = await memory.update_environmental_profile(
            conversation_id, extracted
        )

        # 6. Detect intent
        intents = detect_user_intent(req.message)

        # 7. Check for missing critical information
        missing_questions = get_missing_info(merged_profile, intents)
        should_clarify = needs_clarification(merged_profile, intents)

        if should_clarify and missing_questions:
            # Return clarification request
            clarification_msg = generate_clarification_message(missing_questions)

            await memory.add_message(
                conversation_id, "assistant", clarification_msg,
                metadata={"type": "clarification", "missing": missing_questions}
            )

            return ChatResponse(
                conversation_id=conversation_id,
                message=clarification_msg,
                needs_clarification=True,
                clarification_questions=missing_questions,
                environmental_profile=_clean_profile(merged_profile),
                demo_mode=False,
            )

        # 8. Run reasoning engine
        reasoning_result = generate_reasoning_chain(merged_profile)

        # 9. Run RAG pipeline
        rag_result = rag_pipeline.run(
            query=req.message,
            env_profile=merged_profile,
            active_variables=reasoning_result.get("active_variables", []),
        )
        ranked_docs = rag_result.get("ranked_docs", [])

        # 10. Generate recommendations (LLM or fallback)
        recommendations, summary_msg, is_demo_mode = await generate_recommendations(
            profile=merged_profile,
            reasoning_result=reasoning_result,
            ranked_docs=ranked_docs,
            user_query=req.message,
            llm_provider=llm_provider,
        )

        # 11. Build reasoning trace
        reasoning_trace = build_reasoning_trace(
            merged_profile, reasoning_result, ranked_docs, missing_questions
        )

        # 12. Assemble response message
        if is_demo_mode:
            full_message = f"{DEMO_MODE_NOTICE}\n\n{summary_msg}"
        else:
            full_message = summary_msg

        # 13. Save assistant response
        await memory.add_message(
            conversation_id,
            "assistant",
            full_message,
            metadata={
                "type": "recommendation",
                "demo_mode": is_demo_mode,
                "recommendations_count": len(recommendations),
            },
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message=full_message,
            recommendations=recommendations,
            reasoning_trace=reasoning_trace,
            environmental_profile=_clean_profile(merged_profile),
            needs_clarification=False,
            demo_mode=is_demo_mode,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Return full conversation with messages and environmental profile."""
    conv = await memory.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    context = await memory.get_conversation_context(conversation_id)
    return {
        **conv,
        "messages": context.get("messages", []),
        "environmental_profile": _clean_profile(
            context.get("environmental_profile", {})
        ),
    }


@router.get("/conversations")
async def list_conversations():
    """List all conversations."""
    return await memory.list_conversations()


def _clean_profile(profile: dict) -> dict:
    """Remove None-only nested dicts for cleaner response."""
    if not profile:
        return {}
    cleaned = {}
    for k, v in profile.items():
        if isinstance(v, dict):
            inner = {ik: iv for ik, iv in v.items() if iv is not None}
            if inner:
                cleaned[k] = inner
        elif v is not None:
            cleaned[k] = v
    return cleaned
