# services/rag_services.py - UPDATED VERSION
from typing import Dict, Any, List
from services.ai_llm import AIService
from services.vector_service import VectorService
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, db):
        self.db = db
        self.ai_service = AIService()
        self.vector_service = VectorService()
    
    async def process_call_for_qa_pairs(self, call_sid: str) -> Dict[str, Any]:
        """
        Main method to process a call transcription and generate QA pairs
        """
        try:
            # Get call record with transcription
            call_record = await self.db.Call.find_one({"call_sid": call_sid})
            if not call_record or not call_record.get("call_transcript"):
                call_record = await self.db.AICallLog.find_one({"call_sid": call_sid})
                if not call_record:
                    return {"error": "Call record or transcription not found", "processed": 0}
            
            org_id = call_record["organizationId"]
            print(f"\n\n Organization id: {org_id}\n id type {type(org_id)}\n\n ")

            if not org_id:
                return {"error": "Organization not found for this call", "processed": 0}
            
            # Get organization questions using string org_id
            questions = await self.db.questions.find({"org_id": str(org_id)}).to_list(length=None)
            print(f"\n\n questions {questions} \n\n")
            print(f"\n\n call transcript{call_record.get('call_transcript')}\n\n")

            if not questions:
                return {"error": "No questions found for organization", "processed": 0}
            
            print(f"\n\n call sid: {call_sid}\n\n")

            # Store call transcription in vector database using call_sid as conversation_id
            await self.vector_service.store_conversation(call_sid, call_record["call_transcript"])
            print(f"✅ Stored conversation in vector DB for {call_sid}")
            
            # Process each question and generate QA pairs
            processed_count = 0
            qa_pairs_to_insert = []
            
            for question in questions:
                try:
                    # Extract answer using RAG
                    extraction_result = await self.extract_answer(
                        conversation_id=call_sid,
                        question=question["question_text"],
                        question_lead=question.get("question_keywords", [])
                    )
                    
                    print(f"🔍 Question: {question['question_text']}")
                    print(f"📝 Answer: {extraction_result['answer']}")
                    print(f"📊 Chunks used: {extraction_result['chunks_used']}")
                    
                    # Create QA pair
                    qa_pair = {
                        "org_id": org_id,
                        "conv_id": call_sid,
                        "question": question["question_text"],
                        "answer": extraction_result["answer"],
                        "createdAt": call_record.get("createdAt") or call_record.get("call_started_at")
                    }
                    qa_pairs_to_insert.append(qa_pair)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing question '{question['question_text']}': {e}")
                    continue
            
            # Bulk insert QA pairs - This is the critical point where we save to MongoDB
            if qa_pairs_to_insert:
                try:
                    insert_result = await self.db.qa_pairs.insert_many(qa_pairs_to_insert)
                    print(f"✅ Successfully inserted {len(qa_pairs_to_insert)} QA pairs to MongoDB")
                    
                    # ONLY delete vector database AFTER successful MongoDB insertion
                    # This ensures we don't lose data if MongoDB insertion fails
                    try:
                        deletion_success = await self.vector_service.delete_conversation(call_sid)
                        if deletion_success:
                            print(f"🗑️ Successfully deleted vector database data for conversation {call_sid}")
                        else:
                            logger.warning(f"Failed to delete vector database data for {call_sid} but QA pairs were saved")
                    except Exception as delete_error:
                        # Log the deletion error but don't fail the entire process
                        # since the QA pairs were successfully saved
                        logger.error(f"Error deleting vector data for {call_sid}: {delete_error}")
                        print(f"⚠️ QA pairs saved successfully but failed to clean up vector data for {call_sid}")
                    
                    # Mark call as processed for QA
                    await self.db.Call.update_one(
                        {"call_sid": call_sid},
                        {"$set": {"qa_processed": True, "qa_pairs_count": processed_count}}
                    )
                    
                except Exception as insert_error:
                    logger.error(f"Failed to insert QA pairs to MongoDB: {insert_error}")
                    # Don't delete vector data if MongoDB insertion failed
                    return {"error": f"Failed to save QA pairs: {str(insert_error)}", "processed": 0}
            
            return {
                "success": True,
                "call_sid": call_sid,
                "org_id": str(org_id),
                "processed": processed_count,
                "total_questions": len(questions)
            }
            
        except Exception as e:
            logger.error(f"Error processing lead generation {call_sid} for QA pairs: {e}")
            # Attempt cleanup on general error
            try:
                await self.vector_service.delete_conversation(call_sid)
                print(f"🗑️ Cleaned up vector data for failed conversation {call_sid}")
            except:
                pass
            return {"error": str(e), "processed": 0}
    
    async def extract_answer(self, conversation_id: str, question: str, question_lead: List[str]) -> Dict[str, Any]:
        """Extract answer from call transcription using RAG approach with better error handling"""
        try:
            # Create search query from question and leads
            search_query = f"{question} {' '.join(question_lead)}"
            print(f"🔎 Search query: {search_query}")
            
            # Search for relevant chunks
            relevant_chunks = await self.vector_service.search_similar(
                conversation_id=conversation_id,
                query=search_query,
                top_k=5
            )
            
            print(f"📋 Found {len(relevant_chunks)} relevant chunks")
            
            if not relevant_chunks:
                # Try a fallback: search with just the question
                print("⚠️ No chunks found with leads, trying question only...")
                relevant_chunks = await self.vector_service.search_similar(
                    conversation_id=conversation_id,
                    query=question,
                    top_k=3
                )
                
                if not relevant_chunks:
                    # Last resort: get entire conversation
                    print("⚠️ No chunks found, attempting to get full conversation...")
                    relevant_chunks = await self.vector_service.get_all_chunks(conversation_id)
            
            if not relevant_chunks:
                return {
                    "answer": "No conversation data found for processing.",
                    "leads": question_lead,
                    "chunks_used": 0
                }
            
            # Combine chunks for context (limit to avoid token limits)
            context_pieces = []
            total_length = 0
            max_context_length = 3000  # Adjust based on your token limits
            
            for chunk in relevant_chunks[:5]:  # Max 5 chunks
                chunk_text = chunk["text"]
                if total_length + len(chunk_text) > max_context_length:
                    break
                context_pieces.append(chunk_text)
                total_length += len(chunk_text)
            
            context = "\n\n---\n\n".join(context_pieces)
            print(f"📄 Context length: {len(context)} characters")
            
            # IMPROVED: More flexible LLM prompt
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert at extracting information from call center conversations. 
                    
                    Your task:
                    1. Analyze the provided call transcript context
                    2. Answer the specific question based on what you find
                    3. Be thorough but concise
                    4. If the exact information isn't present, provide the closest relevant information you can find
                    5. Only say "Information not available" if there's truly nothing relevant in the entire context
                    
                    Always provide a helpful response based on the available information."""
                },
                {
                    "role": "user",
                    "content": f"""Call transcript context:
{context}

Question to answer: {question}

Based on the above conversation, please provide a comprehensive answer to the question. Look for any relevant information that addresses the question, even if not explicitly stated."""
                }
            ]
            
            answer = await self.ai_service.chat_completion(messages, temperature=0.1)
            
            # Additional validation
            if not answer or answer.strip().lower() in ['', 'none', 'n/a']:
                answer = f"The call transcript was processed but no specific information was found to answer: {question}"
            
            return {
                "answer": answer.strip(),
                "leads": question_lead,
                "chunks_used": len(context_pieces)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract answer: {e}")
            return {
                "answer": f"Error occurred while processing the question: {question}. Please check the logs for details.",
                "leads": [],
                "chunks_used": 0
            }
        