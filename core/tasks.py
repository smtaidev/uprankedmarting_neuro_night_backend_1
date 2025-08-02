# core/tasks.py
import asyncio
from typing import List, Dict, Any
from services.rag_services import RAGService
from services.lead_generation import LeadGenerationService
from api.models import Question, LeadExtractionResult

async def process_lead_extraction(
    user_id: str, 
    transcript: str, 
    questions: List[Question]
) -> List[LeadExtractionResult]:
    """Process lead extraction for given questions and transcript"""
    rag_service = RAGService()
    lead_service = LeadGenerationService()
    
    # Initialize RAG with transcript
    await rag_service.initialize_with_text(transcript)
    
    results = []
    for question in questions:
        try:
            # Generate leads from question
            leads = await lead_service.generate_leads(question.text)
            
            # Extract values using RAG
            extracted_values = await rag_service.extract_values(leads, question.text)
            
            result = LeadExtractionResult(
                question_id=question.id,
                question_text=question.text,
                leads=leads,
                extracted_values=extracted_values,
                confidence_score=0.8  # Placeholder
            )
            results.append(result)
        except Exception as e:
            print(f"Error processing question {question.id}: {e}")
            
    return results
