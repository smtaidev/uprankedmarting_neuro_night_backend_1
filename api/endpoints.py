# api/endpoints.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uuid
import aiofiles
import os
from pathlib import Path

from api.models import Question, QuestionUpdate, UserSession, ProcessingRequest, LeadExtractionResult
from core.tasks import process_lead_extraction
from core.config import settings

router = APIRouter()

# In-memory storage (in production, use a database)
user_sessions: Dict[str, UserSession] = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process transcript file"""
    if not file.filename.endswith(('.txt', '.text')):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")
    
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate unique user ID
    user_id = str(uuid.uuid4())
    
    try:
        # Read file content
        content = await file.read()
        transcript = content.decode('utf-8')
        
        # Save to uploads directory
        file_path = Path(settings.UPLOAD_DIR) / f"{user_id}_{file.filename}"
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(content)
        
        # Create user session
        session = UserSession(
            user_id=user_id,
            filename=file.filename,
            transcript=transcript
        )
        user_sessions[user_id] = session
        
        return {
            "user_id": user_id,
            "filename": file.filename,
            "transcript_length": len(transcript),
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/session/{user_id}")
async def get_session(user_id: str):
    """Get user session data"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    return {
        "user_id": session.user_id,
        "filename": session.filename,
        "questions": session.questions,
        "results": session.results,
        "transcript_preview": session.transcript[:500] + "..." if len(session.transcript) > 500 else session.transcript
    }

@router.post("/questions/{user_id}")
async def add_question(user_id: str, question: Question):
    """Add a new question"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    session.questions.append(question)
    
    return {"message": "Question added successfully", "question": question}

@router.put("/questions/{user_id}/{question_id}")
async def update_question(user_id: str, question_id: str, question_update: QuestionUpdate):
    """Update an existing question"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    
    for i, q in enumerate(session.questions):
        if q.id == question_id:
            if question_update.text:
                session.questions[i].text = question_update.text
            if question_update.category:
                session.questions[i].category = question_update.category
            return {"message": "Question updated successfully", "question": session.questions[i]}
    
    raise HTTPException(status_code=404, detail="Question not found")

@router.delete("/questions/{user_id}/{question_id}")
async def delete_question(user_id: str, question_id: str):
    """Delete a question"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    
    for i, q in enumerate(session.questions):
        if q.id == question_id:
            deleted_question = session.questions.pop(i)
            return {"message": "Question deleted successfully", "deleted_question": deleted_question}
    
    raise HTTPException(status_code=404, detail="Question not found")

@router.post("/process/{user_id}")
async def process_questions(user_id: str):
    """Process all questions and extract leads"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    
    if not session.questions:
        raise HTTPException(status_code=400, detail="No questions to process")
    
    try:
        # Process lead extraction
        results = await process_lead_extraction(
            user_id=user_id,
            transcript=session.transcript,
            questions=session.questions
        )
        
        session.results = results
        
        return {
            "message": "Processing completed successfully",
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing questions: {str(e)}")

@router.get("/results/{user_id}")
async def get_results(user_id: str):
    """Get processing results"""
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = user_sessions[user_id]
    return {
        "user_id": user_id,
        "results": session.results,
        "total_questions": len(session.questions),
        "processed_questions": len(session.results)
    }
