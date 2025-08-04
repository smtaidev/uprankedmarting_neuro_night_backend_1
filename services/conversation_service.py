# services/conversation_service.py
from typing import List, Dict, Any
import uuid
from bson import ObjectId
from fastapi import HTTPException, UploadFile

from api.models import Conversation
from core.config import settings
from core.tasks import process_conversation
from services.rag_services import RAGService

class ConversationService:
    def __init__(self, db):
        self.db = db
    
    async def upload_conversation(self, domain_id: str, file: UploadFile) -> Dict[str, Any]:
        """Upload conversation file for a specific domain"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            if not file.filename.endswith(('.txt', '.text')):
                raise HTTPException(status_code=400, detail="Only .txt files are allowed")
            
            if file.size > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")
            
            # Check if domain exists
            domain = await self.db.domains.find_one({"_id": ObjectId(domain_id)})
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            # Read file content
            content = await file.read()
            transcript = content.decode('utf-8')
            
            # Create conversation record
            user_session_id = str(uuid.uuid4())
            conversation = Conversation(
                domain_id=ObjectId(domain_id),
                filename=file.filename,
                content=transcript,
                user_session_id=user_session_id
            )
            
            conversation_dict = conversation.dict(by_alias=True)
            result = await self.db.conversations.insert_one(conversation_dict)
            conversation_id = str(result.inserted_id)
            
            # Immediately store in vector database
            try:
                rag_service = RAGService()
                await rag_service.store_conversation(conversation_id, transcript)
            except Exception as e:
                # Log error but don't fail the upload
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to store conversation in vector database: {e}")
            
            return {
                "conversation_id": conversation_id,
                "domain_id": domain_id,
                "domain_name": domain["domain_name"],
                "filename": file.filename,
                "transcript_length": len(transcript),
                "user_session_id": user_session_id,
                "message": "File uploaded successfully - ready for processing"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
    async def process_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Process conversation with domain questions"""
        try:
            if not ObjectId.is_valid(conversation_id):
                raise HTTPException(status_code=400, detail="Invalid conversation ID")
            
            # Get conversation
            conversation = await self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            if conversation["processed"]:
                raise HTTPException(status_code=400, detail="Conversation already processed")
            
            # Get domain info
            domain = await self.db.domains.find_one({"_id": conversation["domain_id"]})
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            # Check if domain has questions
            question_count = await self.db.questions.count_documents({"domain_id": conversation["domain_id"]})
            if question_count == 0:
                raise HTTPException(status_code=400, detail="No questions found for this domain")
            
            # Process conversation
            results = await process_conversation(conversation_id, str(conversation["domain_id"]))
            
            return {
                "conversation_id": conversation_id,
                "domain_name": domain["domain_name"],
                "questions_processed": len(results),
                "results": [
                    {
                        "question_id": str(result.question_id),
                        "question_text": result.question_text,
                        "answer": result.extracted_answer,
                        "confidence": result.confidence_score,
                        "leads": result.leads_detected
                    }
                    for result in results
                ],
                "message": "Conversation processed successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing conversation: {str(e)}")
    
    async def get_conversation_results(self, conversation_id: str) -> Dict[str, Any]:
        """Get processing results for a conversation"""
        try:
            if not ObjectId.is_valid(conversation_id):
                raise HTTPException(status_code=400, detail="Invalid conversation ID")
            
            # Get conversation info
            conversation = await self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Get domain info
            domain = await self.db.domains.find_one({"_id": conversation["domain_id"]})
            
            # Get results
            results_cursor = self.db.results.find({"conversation_id": ObjectId(conversation_id)}).sort("created_at", -1)
            results = await results_cursor.to_list(length=None)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "result_id": str(result["_id"]),
                    "question_id": str(result["question_id"]),
                    "question_text": result["question_text"],
                    "answer": result["extracted_answer"],
                    "confidence": result["confidence_score"],
                    "leads": result["leads_detected"],
                    "created_at": result["created_at"].isoformat()
                })
            
            return {
                "conversation_id": conversation_id,
                "domain_name": domain["domain_name"] if domain else "Unknown",
                "filename": conversation["filename"],
                "processed": conversation["processed"],
                "total_results": len(formatted_results),
                "results": formatted_results
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")
    
    async def get_domain_conversations(self, domain_id: str) -> Dict[str, Any]:
        """Get all conversations for a domain"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            conversations_cursor = self.db.conversations.find({"domain_id": ObjectId(domain_id)}).sort("created_at", -1)
            conversations = await conversations_cursor.to_list(length=None)
            
            result = []
            for conv in conversations:
                # Get result count
                result_count = await self.db.results.count_documents({"conversation_id": conv["_id"]})
                
                result.append({
                    "conversation_id": str(conv["_id"]),
                    "filename": conv["filename"],
                    "processed": conv["processed"],
                    "result_count": result_count,
                    "created_at": conv["created_at"].isoformat(),
                    "content_preview": conv["content"][:200] + "..." if len(conv["content"]) > 200 else conv["content"]
                })
            
            return {"conversations": result}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

