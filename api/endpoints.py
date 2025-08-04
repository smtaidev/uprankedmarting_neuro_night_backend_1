# api/endpoints.py 
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from typing import  Dict, Any

from api.models import DomainCreate, QuestionCreate, QuestionUpdate
from core.database import get_database
from services.domain_service import DomainService
from services.question_service import QuestionService
from services.conversation_service import ConversationService

router = APIRouter()

# Domain endpoints
@router.post("/domains", response_model=Dict[str, Any])
async def create_domain(domain_data: DomainCreate, db=Depends(get_database)):
    """Create a new domain with optional initial questions"""
    domain_service = DomainService(db)
    return await domain_service.create_domain(domain_data)

@router.get("/domains")
async def get_domains(db=Depends(get_database)):
    """Get all domains"""
    domain_service = DomainService(db)
    return await domain_service.get_all_domains()

@router.delete("/domains/{domain_id}")
async def delete_domain(domain_id: str, db=Depends(get_database)):
    """Delete domain and all associated data"""
    domain_service = DomainService(db)
    return await domain_service.delete_domain(domain_id)

@router.post("/domains/{domain_id}/generate-leads")
async def generate_leads_for_domain(domain_id: str, db=Depends(get_database)):
    """Generate key leads for all questions in a domain"""
    domain_service = DomainService(db)
    return await domain_service.generate_leads_for_domain(domain_id)

# Question endpoints
@router.get("/domains/{domain_id}/questions")
async def get_domain_questions(domain_id: str, db=Depends(get_database)):
    """Get all questions for a domain"""
    question_service = QuestionService(db)
    return await question_service.get_domain_questions(domain_id)

@router.post("/domains/{domain_id}/questions")
async def add_question(domain_id: str, question_data: QuestionCreate, db=Depends(get_database)):
    """Add a question to a domain"""
    question_service = QuestionService(db)
    return await question_service.add_question(domain_id, question_data)

@router.put("/questions/{question_id}")
async def update_question(question_id: str, question_data: QuestionUpdate, db=Depends(get_database)):
    """Update a question"""
    question_service = QuestionService(db)
    return await question_service.update_question(question_id, question_data)

@router.delete("/questions/{question_id}")
async def delete_question(question_id: str, db=Depends(get_database)):
    """Delete a question"""
    question_service = QuestionService(db)
    return await question_service.delete_question(question_id)

# Conversation endpoints
@router.post("/domains/{domain_id}/upload")
async def upload_conversation(domain_id: str, file: UploadFile = File(...), db=Depends(get_database)):
    """Upload conversation file for a specific domain"""
    conversation_service = ConversationService(db)
    return await conversation_service.upload_conversation(domain_id, file)

@router.post("/conversations/{conversation_id}/process")
async def process_conversation_endpoint(conversation_id: str, db=Depends(get_database)):
    """Process conversation with domain questions"""
    conversation_service = ConversationService(db)
    return await conversation_service.process_conversation(conversation_id)

@router.get("/conversations/{conversation_id}/results")
async def get_conversation_results(conversation_id: str, db=Depends(get_database)):
    """Get processing results for a conversation"""
    conversation_service = ConversationService(db)
    return await conversation_service.get_conversation_results(conversation_id)

@router.get("/domains/{domain_id}/conversations")
async def get_domain_conversations(domain_id: str, db=Depends(get_database)):
    """Get all conversations for a domain"""
    conversation_service = ConversationService(db)
    return await conversation_service.get_domain_conversations(domain_id)




