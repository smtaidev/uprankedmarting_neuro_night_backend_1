# api/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from uuid import uuid4

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str = Field(..., min_length=5, max_length=500)
    category: Optional[str] = Field(default="general")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Question text cannot be empty')
        return v.strip()

class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=5, max_length=500)
    category: Optional[str] = None

class LeadExtractionResult(BaseModel):
    question_id: str
    question_text: str
    leads: List[str]
    extracted_values: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class UserSession(BaseModel):
    user_id: str
    filename: str
    transcript: str
    questions: List[Question] = Field(default_factory=list)
    results: List[LeadExtractionResult] = Field(default_factory=list)

class ProcessingRequest(BaseModel):
    user_id: str
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()
