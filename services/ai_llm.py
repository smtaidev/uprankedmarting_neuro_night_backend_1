# services/ai_llm.py
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from core.config import settings

class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not provided")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        messages = [
            {"role": "system", "content": "Extract 5-10 key terms/phrases from the following text that would be useful for information retrieval. Return only the keywords, separated by commas."},
            {"role": "user", "content": text}
        ]
        
        response = await self.chat_completion(messages)
        return [kw.strip() for kw in response.split(",") if kw.strip()]
