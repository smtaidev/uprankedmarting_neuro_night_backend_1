# services/lead_generation.py
from typing import List
from services.ai_llm import AIService

class LeadGenerationService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_leads(self,organization_name, question: str) -> List[str]:
        """Generate lead terms/variables from a question"""
        messages = [
            {
                "role": "system", 
                "content": f"""You are an expert at identifying most relevant unique key variables and terms that would help extract information from call center transcripts for a specific organization.
                Given a question, identify the unique key terms, phrases, or variable names but one term/phrase/variable name
                should not conflict with each others informations. Return only the terms or variable name. If there is a phrase provide an underscore between words. If the question is irrelevent response with "Provide a relevant Question" nothing else. """
            },
            {
                "role": "user", 
                "content": f"Organization Name: {organization_name}\n\nQuestion: {question}\n\nidentify the key terms/variables from the question"
            }
        ]
        response = await self.ai_service.chat_completion(messages)
        leads = [lead.strip() for lead in response.split(",") if lead.strip()]
        return leads[:3]


