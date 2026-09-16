from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    title = Column(String)
    action = Column(Text)
    reasoning = Column(Text)
    impacted_metrics_json = Column(JSON)
    time_horizon = Column(String)
    confidence = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class EvidenceSource(Base):
    __tablename__ = "evidence_sources"
    id = Column(String, primary_key=True)
    recommendation_id = Column(String, ForeignKey("recommendations.id"))
    title = Column(String)
    source_org = Column(String)
    year = Column(String)
    url = Column(String)
    topic = Column(String)
    variables_json = Column(JSON)
    evidence_type = Column(String)
    supporting_excerpt = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
