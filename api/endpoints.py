# api/endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import asyncio
import logging

from api.models import *
from core.database import get_database
from core.rate_limiter import RateLimiter
from core.circuit_breaker import CircuitBreaker
from services.ai_llm import AIService
from services.qa_retrieval_service import QARetrievalService
from services.rag_services import RAGService

router = APIRouter()
logger = logging.getLogger(__name__)

# Shared instances
rate_limiter = RateLimiter(requests_per_minute=100)
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

# Helper function for AI validation
async def validate_question_with_ai(industry: str, question: str, existing_text: str):
    """Centralized AI validation logic"""
    ai_service = AIService()
    validation_result = await ai_service.question_ai_validation_check(industry, question, existing_text)
    
    if validation_result[0] == 'Provide a relevant Question':
        return {"accepted": False, "reason": "Provide a relevant Question to your organization", "keywords": []}
    elif validation_result[0] == '0':
        return {"accepted": False, "reason": "Similar question already exists", "keywords": []}
    else:
        return {"accepted": True, "keywords": validation_result}

# Common response builder
def build_question_response(accepted: bool, question: str, org_id: str, **kwargs):
    """Build standardized question response"""
    return {
        "accepted": accepted,
        "question": question,
        "org_id": org_id,
        **kwargs
    }

@router.post("/organizations/{org_id}/questions", response_model=Dict[str, Any])
async def add_single_question(org_id: str, question_data: SingleQuestionCreate, db=Depends(get_database)):
    """Add a single question to an organization"""
    async with rate_limiter.acquire(f"question_{org_id}"), circuit_breaker.call():
        if question_data.org_id != org_id:
            raise HTTPException(status_code=400, detail="org_id mismatch")
        
        # Create/get organization
        existing_org = await db.organizations.find_one({"_id": ObjectId(org_id)})
        if not existing_org:
            raise HTTPException(status_code=400,detail="organization does not exists")
        
        # AI validation
        existing_questions = await db.questions.find({"org_id": org_id}).to_list(length=None)
        existing_text = " ".join([q["question_text"] for q in existing_questions])
        validation = await validate_question_with_ai(existing_org["name"], question_data.question, existing_text)
        
        if not validation["accepted"]:
            return build_question_response(False, question_data.question, org_id, 
                                         reason=validation["reason"])
        
        # Save question
        question = Question(org_id=org_id, question_text=question_data.question, 
                          question_keywords=validation["keywords"])
        q_result = await db.questions.insert_one(question.dict(by_alias=True))
        
        return build_question_response(True, question_data.question, org_id,
                                     question_id=str(q_result.inserted_id),
                                     keywords=validation["keywords"],
                                     message=f"Question added Sucessfully")

@router.delete("/organizations/{org_id}/questions/{question_id}", response_model=Dict[str, Any])
async def delete_question(org_id: str, question_id: str, db=Depends(get_database)):
    """Delete a question from an organization"""
    async with rate_limiter.acquire(f"question_delete_{org_id}_{question_id}"):
        from bson import ObjectId
        
        try:
            question_obj_id = ObjectId(question_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid question_id format")
        
        question = await db.questions.find_one({"_id": question_obj_id, "org_id": org_id})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        result = await db.questions.delete_one({"_id": question_obj_id, "org_id": org_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"message": "Question deleted successfully", "question_id": question_id, 
                "org_id": org_id, "deleted_question": question["question_text"]}

@router.put("/organizations/{org_id}/questions/{question_id}", response_model=Dict[str, Any])
async def update_question(org_id: str, question_id: str, question_update: QuestionUpdate, db=Depends(get_database)):
    """Update a question with AI validation"""
    async with rate_limiter.acquire(f"question_update_{org_id}_{question_id}"), circuit_breaker.call():
        from bson import ObjectId
        from datetime import datetime
        
        try:
            question_obj_id = ObjectId(question_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid question_id format")
        
        existing_question = await db.questions.find_one({"_id": question_obj_id, "org_id": org_id})
        if not existing_question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        org = await db.organizations.find_one({"org_id": org_id, "is_active": True})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Get other questions for validation
        other_questions = await db.questions.find({"org_id": org_id, "_id": {"$ne": question_obj_id}}).to_list(length=None)
        existing_text = " ".join([q["question_text"] for q in other_questions])
        
        # AI validation
        validation = await validate_question_with_ai(org["industry"], question_update.question, existing_text)
        
        if not validation["accepted"]:
            return build_question_response(False, question_update.question, org_id,
                                         reason=validation["reason"], question_id=question_id,
                                         original_question=existing_question["question_text"])
        
        # Update question
        update_result = await db.questions.update_one(
            {"_id": question_obj_id, "org_id": org_id},
            {"$set": {"question_text": question_update.question, "question_keywords": validation["keywords"],
                     "updated_at": datetime.utcnow()}}
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return build_question_response(True, question_update.question, org_id,
                                     question_id=question_id, original_question=existing_question["question_text"],
                                     keywords=validation["keywords"], message="Question updated successfully")

@router.get("/organizations/{org_id}/questions", response_model=List[Dict[str, Any]])
async def get_organization_questions(org_id: str, db=Depends(get_database)):
    """Get all questions for an organization"""
    async with rate_limiter.acquire(f"questions_get_{org_id}"):
        org = await db.organizations.find_one({"_id": ObjectId(org_id)})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        questions = await db.questions.find({"org_id": org_id}).to_list(length=None)
        # print(questions)
        
        return [{
            "question_id": str(q["_id"]),
            "question_text": q["question_text"],
            "question_keywords": q.get("question_keywords", []),
            "created_at": q["created_at"].isoformat(),
            "updated_at": q.get("updated_at").isoformat() if q.get("updated_at") else None
        } for q in questions]

@router.post("/organizations/conversations/", response_model=Dict[str, Any])
async def process_conversation(call_sid: str, db=Depends(get_database)):
    rag_service = RAGService(db)
    result = await rag_service.process_call_for_qa_pairs(call_sid)
    logger.info(f"QA processing result: {result}")
    return result


@router.get("/organizations/{org_id}/conversations/{conv_id}/qa-pairs", response_model=List[QAResponse])
async def get_qa_pairs(org_id: str, conv_id: str, db=Depends(get_database)):
    """Get question-answer pairs for a conversation"""
    async with rate_limiter.acquire(f"qa_get_{org_id}_{conv_id}"):
        qa_service = QARetrievalService(db)
        return await qa_service.get_qa_pairs(org_id, conv_id)
    
