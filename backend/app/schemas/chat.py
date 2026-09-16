from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None

class EvidenceItem(BaseModel):
    title: str
    source: str
    year: Optional[int] = None
    url: Optional[str] = None
    supporting_excerpt: str
    topic: Optional[str] = None
    variables: Optional[List[str]] = None

class RecommendationItem(BaseModel):
    title: str
    action: str
    reasoning: str
    impacted_metrics: List[str]
    time_horizon: str
    confidence: str
    evidence: List[EvidenceItem]

class ReasoningTrace(BaseModel):
    variables_detected: List[str]
    missing_variables: List[str]
    retrieved_evidence_count: int
    environmental_relationships: List[str]
    evidence_titles: List[str]

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    recommendations: Optional[List[RecommendationItem]] = None
    reasoning_trace: Optional[ReasoningTrace] = None
    environmental_profile: Optional[dict] = None
    needs_clarification: bool = False
    clarification_questions: Optional[List[str]] = None
    demo_mode: bool = False
