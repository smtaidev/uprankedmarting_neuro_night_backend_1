# services/lead_generation.py
from typing import List
from services.ai_llm import AIService

class LeadGenerationService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_leads(self, question: str) -> List[str]:
        """Generate lead terms/variables from a question"""
        messages = [
            {
                "role": "system", 
                "content": "You are an expert at identifying key variables and terms that would help extract information from call center transcripts. Given a question, identify 3-5 key terms, phrases, or variable names that would be most relevant for finding the answer in a conversation transcript. Return only the terms, separated by commas."
            },
            {
                "role": "user", 
                "content": f"Question: {question}\n\nWhat are the key terms/variables to look for?"
            }
        ]
        
        response = await self.ai_service.chat_completion(messages)
        leads = [lead.strip() for lead in response.split(",") if lead.strip()]
        return leads[:5]  # Limit to 5 leads
