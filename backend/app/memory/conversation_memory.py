"""
Conversation memory: SQLite-backed multi-turn state.
Persists messages, environmental profiles, and conversation context.
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.conversation import Conversation, Message, User
from app.models.environmental import EnvironmentalProfile as DBEnvironmentalProfile

logger = logging.getLogger(__name__)


class ConversationMemory:
    """SQLite-backed conversation memory manager."""

    async def create_conversation(
        self, session_id: Optional[str] = None, title: Optional[str] = None
    ) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        if not session_id:
            session_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as db:
            # Ensure user/session exists
            existing = await db.execute(
                select(User).where(User.session_id == session_id)
            )
            if not existing.scalar_one_or_none():
                user = User(id=str(uuid.uuid4()), session_id=session_id)
                db.add(user)

            conv = Conversation(
                id=conversation_id,
                session_id=session_id,
                title=title or "New Conversation",
            )
            db.add(conv)
            await db.commit()

        return conversation_id

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add a message to the conversation. Returns message ID."""
        message_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as db:
            msg = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata_json=metadata or {},
            )
            db.add(msg)

            # Update conversation updated_at
            await db.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )
            await db.commit()
        return message_id

    async def get_messages(self, conversation_id: str) -> list[dict]:
        """Return all messages in a conversation, ordered by creation time."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            messages = result.scalars().all()
            return [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "metadata": m.metadata_json or {},
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ]

    async def update_environmental_profile(
        self, conversation_id: str, partial_profile: dict
    ) -> dict:
        """
        Merge a partial environmental profile into the stored profile.
        Never overwrites existing values with None/empty.
        Returns the merged profile.
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBEnvironmentalProfile).where(
                    DBEnvironmentalProfile.conversation_id == conversation_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                existing = DBEnvironmentalProfile(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                )
                db.add(existing)

            # Merge flat fields
            self._merge_profile_fields(existing, partial_profile)
            await db.commit()
            await db.refresh(existing)

        return self._profile_to_dict(existing)

    def _merge_profile_fields(
        self, existing: DBEnvironmentalProfile, partial: dict
    ) -> None:
        """Update DB model fields from partial profile dict, never overwriting with None."""

        def _set_if_new(obj, field: str, value):
            if value is not None and value != "":
                setattr(obj, field, value)

        _set_if_new(existing, "region", partial.get("region"))
        _set_if_new(existing, "latitude", partial.get("latitude"))
        _set_if_new(existing, "longitude", partial.get("longitude"))

        soil = partial.get("soil") or {}
        _set_if_new(existing, "soil_ph", soil.get("ph"))
        _set_if_new(
            existing, "soil_organic_carbon_percent", soil.get("organic_carbon_percent")
        )
        _set_if_new(existing, "soil_moisture_percent", soil.get("moisture_percent"))
        _set_if_new(existing, "soil_structure", soil.get("structure"))
        _set_if_new(
            existing, "soil_nutrient_availability", soil.get("nutrient_availability")
        )

        lu = partial.get("land_use") or {}
        _set_if_new(existing, "land_use_primary_type", lu.get("primary_type"))
        _set_if_new(existing, "land_use_cropping_system", lu.get("cropping_system"))
        _set_if_new(existing, "land_use_crop", lu.get("crop"))

        bd = partial.get("biodiversity") or {}
        _set_if_new(
            existing, "biodiversity_species_richness", bd.get("species_richness")
        )
        _set_if_new(
            existing, "biodiversity_habitat_diversity", bd.get("habitat_diversity")
        )
        _set_if_new(
            existing,
            "biodiversity_pollinator_presence",
            bd.get("pollinator_presence"),
        )
        _set_if_new(
            existing,
            "biodiversity_native_vegetation",
            bd.get("native_vegetation_percent"),
        )
        _set_if_new(
            existing,
            "biodiversity_connectivity",
            bd.get("ecological_connectivity"),
        )

        cl = partial.get("climate") or {}
        _set_if_new(existing, "climate_temperature_c", cl.get("temperature_c"))
        _set_if_new(existing, "climate_rainfall_mm", cl.get("rainfall_mm"))
        _set_if_new(existing, "climate_rainfall_pattern", cl.get("rainfall_pattern"))
        _set_if_new(existing, "climate_seasonality", cl.get("seasonality"))
        if cl.get("drought_conditions") is not None:
            existing.climate_drought_conditions = cl["drought_conditions"]

        hi = partial.get("human_impact") or {}
        _set_if_new(
            existing, "human_impact_pollution_level", hi.get("pollution_level")
        )
        _set_if_new(
            existing,
            "human_impact_pesticide_pressure",
            hi.get("pesticide_pressure"),
        )
        _set_if_new(
            existing,
            "human_impact_deforestation_pressure",
            hi.get("deforestation_pressure"),
        )
        _set_if_new(
            existing,
            "human_impact_habitat_disturbance",
            hi.get("habitat_disturbance"),
        )

    def _profile_to_dict(self, p: DBEnvironmentalProfile) -> dict:
        """Convert DB model to nested dict matching the schema."""
        return {
            "region": p.region,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "soil": {
                "ph": p.soil_ph,
                "organic_carbon_percent": p.soil_organic_carbon_percent,
                "moisture_percent": p.soil_moisture_percent,
                "structure": p.soil_structure,
                "nutrient_availability": p.soil_nutrient_availability,
            },
            "land_use": {
                "primary_type": p.land_use_primary_type,
                "cropping_system": p.land_use_cropping_system,
                "crop": p.land_use_crop,
            },
            "biodiversity": {
                "species_richness": p.biodiversity_species_richness,
                "habitat_diversity": p.biodiversity_habitat_diversity,
                "pollinator_presence": p.biodiversity_pollinator_presence,
                "native_vegetation_percent": p.biodiversity_native_vegetation,
                "ecological_connectivity": p.biodiversity_connectivity,
            },
            "climate": {
                "temperature_c": p.climate_temperature_c,
                "rainfall_mm": p.climate_rainfall_mm,
                "rainfall_pattern": p.climate_rainfall_pattern,
                "seasonality": p.climate_seasonality,
                "drought_conditions": p.climate_drought_conditions,
            },
            "human_impact": {
                "pollution_level": p.human_impact_pollution_level,
                "pesticide_pressure": p.human_impact_pesticide_pressure,
                "deforestation_pressure": p.human_impact_deforestation_pressure,
                "habitat_disturbance": p.human_impact_habitat_disturbance,
            },
        }

    async def get_environmental_profile(self, conversation_id: str) -> dict:
        """Return the stored environmental profile for a conversation."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DBEnvironmentalProfile).where(
                    DBEnvironmentalProfile.conversation_id == conversation_id
                )
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                return {}
            return self._profile_to_dict(existing)

    async def get_conversation_context(self, conversation_id: str) -> dict:
        """Return messages + environmental profile for a conversation."""
        messages = await self.get_messages(conversation_id)
        profile = await self.get_environmental_profile(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "environmental_profile": profile,
        }

    async def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            return result.scalar_one_or_none() is not None

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Return conversation metadata."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conv = result.scalar_one_or_none()
            if not conv:
                return None
            return {
                "id": conv.id,
                "session_id": conv.session_id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
            }

    async def list_conversations(self, session_id: Optional[str] = None) -> list[dict]:
        """List conversations, optionally filtered by session."""
        async with AsyncSessionLocal() as db:
            stmt = select(Conversation).order_by(Conversation.updated_at.desc())
            if session_id:
                stmt = stmt.where(Conversation.session_id == session_id)
            result = await db.execute(stmt)
            convs = result.scalars().all()
            return [
                {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in convs
            ]
