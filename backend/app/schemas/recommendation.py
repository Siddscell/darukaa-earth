from pydantic import BaseModel
from typing import Optional
from .environmental import EnvironmentalProfile

class RecommendationRequest(BaseModel):
    profile: EnvironmentalProfile
    query: Optional[str] = None
