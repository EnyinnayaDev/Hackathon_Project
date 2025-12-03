from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None  # For tracking conversations

class AnswerResponse(BaseModel):
    answer: str
    source: str = "CampusAI"
    conversation_id: Optional[str] = None
    related_topics: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    node_service_connected: bool