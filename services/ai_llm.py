# services/ai_llm.py

from openai import AsyncOpenAI
from typing import List, Dict, Any
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not provided")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,timeout=60.0)

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = settings.OPENAI_MODEL,
        temperature: float = 0.0
    ) -> str:
        """
        Perform a chat completion call using OpenAI's API.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
                # timeout=30.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""

    async def question_ai_validation_check(
        self,
        industry_name: str,
        new_question: str,
        existing_questions: str
    ) -> List[str]:
        """
        Checks whether a new question already exists in a given list of existing questions,
        and extracts key terms if it's new and relevant to questions a call center agent might ask a caller.

        Returns:
            - ["0"] if the question already exists
            - ["Provide a relevant Question"] if irrelevant
            - [keyword1, keyword2, ...] otherwise
        """

        system_prompt = (
            "You are a helpful assistant for validating new call center questions based on an industry context. "
            "Use broad, inclusive reasoning when determining relevance.\n\n"
            "Step 1: Check if the existing questions list has any meaningful content.\n"
            "Step 2: If there are existing questions, check if the new question is clearly very similar to one of them. "
            "If yes, respond with: '0'\n"
            "Step 3: If not similar or no existing questions, check if the new question could reasonably apply within the given industry. "
            "This includes any business, customer service, product, or operational topic that could occur in that field.\n"
            "Step 4: If the question is clearly unrelated to the industry or business context (like trivia or irrelevant opinions), return: 'Provide a relevant Question'\n"
            "Step 5: Otherwise, extract key terms from the new question (use underscores for multi-word phrases) and return those only — no extra text."
        )


        user_prompt = (
            f"Industry: {industry_name}\n\n"
            f"New question: {new_question}\n\n"
            f"Existing questions: '{existing_questions}'\n\n"
            "Please validate the new question based on the following relaxed logic:\n"
            "1. Are there any meaningful existing questions? (Ignore if empty/whitespace)\n"
            "2. If yes, is the new question very similar to any of them? If so, return '0'\n"
            "3. If not, does the new question make reasonable sense in the context of the given industry — for example, relating to business operations, customer interactions, products, services, or internal processes?\n"
            "4. If it's clearly irrelevant to the industry or to any reasonable business interaction, return 'Provide a relevant Question'\n"
            "5. Otherwise, extract keywords from the new question (use underscore_separated if needed) and return those only."
        )


        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.chat_completion(messages)

        if response.strip() in ["0", "Provide a relevant Question"]:
            return [response.strip()]

        return [kw.strip() for kw in response.split(",") if kw.strip()]
    