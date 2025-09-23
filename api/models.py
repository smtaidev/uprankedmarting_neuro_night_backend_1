# api/models.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
import uuid
from enum import Enum

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

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Base model with common config
class BaseMongoModel(BaseModel):
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,  # Automatically convert ObjectId to string
            datetime: lambda v: v.isoformat()  # Ensure datetime serialization
        }

# Simplified question validation
def validate_text_field(v, min_len=3, max_len=500):
    if len(v.strip()) < min_len:
        raise ValueError(f'Text must be at least {min_len} characters long')
    return v.strip()

class Question(BaseMongoModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    org_id: str = Field(...)
    question_text: str = Field(..., min_length=3, max_length=500)
    question_keywords: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class SingleQuestionCreate(BaseModel):
    org_id: str = Field(..., min_length=1, max_length=50)
    question: str = Field(..., min_length=3, max_length=500)
    # org_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('question')
    def validate_question(cls, v):
        return validate_text_field(v, 3, 500)

class QuestionUpdate(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    
    @field_validator('question')
    def validate_question(cls, v):
        return validate_text_field(v, 3, 500)


class Conversation(BaseMongoModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    org_id: str = Field(...)
    conv_id: str = Field(...)
    conv_script: str = Field(...)
    processed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QAPair(BaseMongoModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    org_id: str = Field(...)
    conv_id: str = Field(...)
    question: str = Field(...)
    answer: str = Field(...)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class QAResponse(BaseModel):
    question: str
    answer: str
    createdAt: str
