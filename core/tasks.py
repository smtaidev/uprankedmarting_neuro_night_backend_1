# core/tasks.py
import asyncio
from typing import List
from bson import ObjectId
from api.models import Question, ProcessingResult
from services.rag_services import RAGService
from core.database import get_database
import logging

logger = logging.getLogger(__name__)

async def process_conversation(conversation_id: str, domain_id: str) -> List[ProcessingResult]:
    """Process conversation with all questions from the domain"""
    try:
        db = await get_database()
        rag_service = RAGService()
        
        # Get conversation
        conversation = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Store conversation in vector database if not already stored
        try:
            await rag_service.store_conversation(conversation_id, conversation["content"])
        except Exception as e:
            logger.warning(f"Conversation might already be stored in vector DB: {e}")
        
        # Get all questions for the domain
        questions_cursor = db.questions.find({"domain_id": ObjectId(domain_id)})
        questions = await questions_cursor.to_list(length=None)
        
        results = []
        for question_doc in questions:
            # print(f"Question Doc: \n{question_doc}")
            try:
                # Extract answer using RAG
                extraction_result = await rag_service.extract_answer(
                    conversation_id=conversation_id,
                    question=question_doc["question_text"],
                    question_lead=question_doc["question_lead"]
                )
                
                # Ensure confidence is valid
                confidence = max(0.0, min(extraction_result.get("confidence", 0.0), 1.0))
                
                # Create result document
                result = ProcessingResult(
                    conversation_id=ObjectId(conversation_id),
                    question_id=question_doc["_id"],
                    question_text=question_doc["question_text"],
                    extracted_answer=extraction_result["answer"],
                    confidence_score=confidence,
                    leads_detected=extraction_result.get("leads", [])
                )
                
                # Save to database
                result_dict = result.dict(by_alias=True)
                await db.results.insert_one(result_dict)
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing question {question_doc['_id']}: {e}")
                # Create a default result for failed questions
                try:
                    default_result = ProcessingResult(
                        conversation_id=ObjectId(conversation_id),
                        question_id=question_doc["_id"],
                        question_text=question_doc["question_text"],
                        extracted_answer="Error occurred during processing",
                        confidence_score=0.0,
                        leads_detected=[]
                    )
                    result_dict = default_result.dict(by_alias=True)
                    await db.results.insert_one(result_dict)
                    results.append(default_result)
                except Exception as nested_e:
                    logger.error(f"Failed to create default result: {nested_e}")
                continue
        # Mark conversation as processed
        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"processed": True}}
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing conversation {conversation_id}: {e}")
        raise



