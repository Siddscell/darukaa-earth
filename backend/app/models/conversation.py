from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    session_id = Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now())

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True)
    session_id = Column(String)
    title = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class RetrievalEvent(Base):
    __tablename__ = "retrieval_events"
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    query = Column(Text)
    retrieved_doc_ids_json = Column(JSON)
    scores_json = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
