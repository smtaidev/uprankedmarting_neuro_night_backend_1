# services/rag_services.py
from typing import Dict, Any
from services.ai_llm import AIService
from services.vector_service import VectorService
from services.lead_generation import LeadGenerationService
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.ai_service = AIService()
        self.vector_service = VectorService()
        self.lead_service = LeadGenerationService()
    
    async def store_conversation(self, conversation_id: str, content: str):
        """Store conversation in vector database"""
        await self.vector_service.store_conversation(conversation_id, content)

    async def extract_answer(self, conversation_id: str, question: str, question_lead) -> Dict[str, Any]:
        """Extract answer from conversation using RAG approach"""
        try:

            # Create search query from question and leads
            search_query = f"{question} {' '.join(question_lead)}"
            
            # Search for relevant chunks
            relevant_chunks = await self.vector_service.search_similar(
                conversation_id=conversation_id,
                query=search_query,
                top_k=5
            )
            
            if not relevant_chunks:
                return {
                    "answer": "No relevant information found in the conversation.",
                    "confidence": 0.0,
                    "leads": question_lead,
                    "chunks_used": 0
                }
            
            # Combine chunks for context
            context = "\n\n".join([chunk["text"] for chunk in relevant_chunks])
            
            # Generate answer using LLM
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at extracting specific information from call center conversations. Given a context from a conversation and a question, provide a concise and accurate answer. If the information is not clearly present, say 'Information not available in the conversation'."
                },
                {
                    "role": "user",
                    "content": f"Context from conversation:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                }
            ]
            
            answer = await self.ai_service.chat_completion(messages)
            
            # Calculate confidence based on similarity scores and chunk count
            avg_similarity = sum(chunk["similarity"] for chunk in relevant_chunks) / len(relevant_chunks)
            confidence = max(0.0, min(avg_similarity * 1.2, 1.0))  # Boost similarity score slightly
            
            return {
                "answer": answer.strip(),
                "confidence": confidence,
                "leads": question_lead,
                "chunks_used": len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract answer: {e}")
            return {
                "answer": "Error occurred during processing.",
                "confidence": 0.0,
                "leads": [],
                "chunks_used": 0
            }


