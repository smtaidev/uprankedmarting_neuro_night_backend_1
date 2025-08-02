# services/rag_service.py
import re
from typing import List, Dict, Any
from services.ai_llm import AIService

class RAGService:
    def __init__(self):
        self.ai_service = AIService()
        self.chunks = []
        self.text = ""
    
    async def initialize_with_text(self, text: str):
        """Initialize RAG service with transcript text"""
        self.text = text
        self.chunks = self._chunk_text(text)
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _search_chunks(self, leads: List[str], top_k: int = 3) -> List[str]:
        """Simple keyword-based chunk retrieval"""
        scored_chunks = []
        
        for chunk in self.chunks:
            score = 0
            chunk_lower = chunk.lower()
            
            for lead in leads:
                lead_lower = lead.lower()
                # Count occurrences of lead terms
                score += chunk_lower.count(lead_lower)
                # Bonus for exact matches
                if lead_lower in chunk_lower:
                    score += 2
        
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top chunks
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored_chunks[:top_k]]
    
    async def extract_values(self, leads: List[str], question: str) -> Dict[str, Any]:
        """Extract values using RAG approach"""
        # Retrieve relevant chunks
        relevant_chunks = self._search_chunks(leads)
        
        if not relevant_chunks:
            return {"answer": "No relevant information found", "confidence": 0.0}
        
        # Combine chunks for context
        context = "\n\n".join(relevant_chunks)
        
        # Use LLM to extract answer from context
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting specific information from call center conversations. Given a context from a conversation and a question, provide a concise and accurate answer. If the information is not clearly present, say 'Information not found'."
            },
            {
                "role": "user",
                "content": f"Context from conversation:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            }
        ]
        
        answer = await self.ai_service.chat_completion(messages)
        
        # Calculate simple confidence based on keyword matches
        confidence = min(len(relevant_chunks) * 0.3, 1.0)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "context_used": len(relevant_chunks),
            "leads_matched": leads
        }
