# api/models.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(type="string")
        return schema

class Domain(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    domain_name: str = Field(..., min_length=2, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DomainCreate(BaseModel):
    domain_name: str = Field(..., min_length=2, max_length=100)
    questions: Optional[List[str]] = Field(default=[])

class Question(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    domain_id: PyObjectId = Field(...)
    question_text: str = Field(..., min_length=3, max_length=500)
    question_lead: Optional[List[str]] = Field(default=[])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=3, max_length=500)

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=3, max_length=500)

class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    domain_id: PyObjectId = Field(...)
    filename: str = Field(...)
    content: str = Field(...)
    user_session_id: str = Field(...)
    processed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProcessingResult(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: PyObjectId = Field(...)
    question_id: PyObjectId = Field(...)
    question_text: str = Field(...)
    extracted_answer: str = Field(...)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    leads_detected: List[str] = Field(default=[])
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


