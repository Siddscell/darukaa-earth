"""
Environment router: store and retrieve environmental profiles.
"""
import uuid
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.environmental import EnvironmentalProfileCreate
from app.memory.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)
router = APIRouter()
memory = ConversationMemory()


@router.post("/environment/profile")
async def create_or_update_profile(profile: EnvironmentalProfileCreate):
    """Create or update an environmental profile for a conversation."""
    try:
        conversation_id = profile.conversation_id
        if not conversation_id:
            conversation_id = await memory.create_conversation(
                title="Environmental Profile Session"
            )

        profile_dict = profile.model_dump(exclude={"conversation_id"}, exclude_none=True)
        merged = await memory.update_environmental_profile(conversation_id, profile_dict)

        return {
            "status": "success",
            "conversation_id": conversation_id,
            "profile": merged,
        }
    except Exception as e:
        logger.error(f"Profile creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environment/profile/{conversation_id}")
async def get_profile(conversation_id: str):
    """Return stored environmental profile."""
    exists = await memory.conversation_exists(conversation_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Conversation not found")

    profile = await memory.get_environmental_profile(conversation_id)
    return {"conversation_id": conversation_id, "profile": profile}
