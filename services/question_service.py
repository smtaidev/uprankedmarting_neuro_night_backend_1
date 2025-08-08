# services/question_service.py
from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException
import logging

from api.models import Question, QuestionCreate, QuestionUpdate
from services.lead_generation import LeadGenerationService

class QuestionService:
    def __init__(self, db):
        self.db = db
    
    async def get_domain_questions(self, domain_id: str) -> Dict[str, Any]:
        """Get all questions for a domain"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            questions_cursor = self.db.questions.find({"domain_id": ObjectId(domain_id)}).sort("created_at", -1)
            questions = await questions_cursor.to_list(length=None)
            
            result = []
            for question in questions:
                result.append({
                    "id": str(question["_id"]),
                    "question_text": question["question_text"],
                    "question_lead": question.get("question_lead", []),
                    "created_at": question["created_at"].isoformat()
                })
            
            return {"questions": result}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")
    

    async def add_question(self, domain_id: str, question: QuestionCreate) -> Dict[str, Any]:
        """Check for redundant questions and add if not redundant"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            domain_obj_id = ObjectId(domain_id)
            
            # Check if domain exists
            domain = await self.db.domains.find_one({"_id": domain_obj_id})
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            domain_name = domain.get("domain_name")
            
            # Get all questions for the domain
            questions = await self.db.questions.find({"domain_id": ObjectId(domain_id)}).to_list(length=None)

            # Combine all question texts
            all_questions_text = " ".join([q["question_text"] for q in questions])

            from services.ai_llm import AIService
            ai_service = AIService()

            # Checks whether a new question already exists in a given list of existing questions,and extracts key terms if it's new and relevant.
            key_variable = await ai_service.question_ai_validation_check(domain_name, question.question_text.strip().lower(),all_questions_text.strip().lower())

            # print(f"AI Service returned: {key_variable}")
            # print(f"Type of key_variable: {type(key_variable)}")
            # print(f"First element: {key_variable[0] if key_variable else 'None'}")

            if key_variable[0] == 'Provide a relevant Question':
                return {"message": key_variable}
            elif key_variable[0] == '0':
                return {"message": "Same type of question already exists"}
            else:
                # print(f"About to save question_lead: {key_variable}")
                
                domain_obj_id = ObjectId(domain_id)
                # Ensure key_variable is a list
                if not isinstance(key_variable, list):
                    key_variable = [key_variable] if key_variable else []
                
                # Create question
                question_obj = Question(
                    domain_id=domain_obj_id,
                    question_text=question.question_text,
                    question_lead=key_variable
                )
                
                # print(f"Question object before save: {question_obj.dict()}")
                
                question_dict = question_obj.dict(by_alias=True)
                result = await self.db.questions.insert_one(question_dict)
                return {
                "id": str(result.inserted_id),
                "question_text": question.question_text,
                "question_lead": key_variable,
                "message": "Question added successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in redundant question checking: {str(e)}")

    async def update_question(self, question_id: str, question_data: QuestionUpdate) -> Dict[str, str]:
        """Update a question"""
        try:
            if not ObjectId.is_valid(question_id):
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            update_data = {}
            if question_data.question_text:
                update_data["question_text"] = question_data.question_text
                
                # If question text is updated, regenerate leads
                question = await self.db.questions.find_one({"_id": ObjectId(question_id)})
                if question:
                    domain = await self.db.domains.find_one({"_id": question["domain_id"]})
                    if domain:
                        # Get existing questions for validation
                        questions = await self.db.questions.find({"domain_id": question["domain_id"]}).to_list(length=None)
                        all_questions_text = " ".join([q["question_text"] for q in questions if str(q["_id"]) != question_id])
                        
                        from services.ai_llm import AIService
                        ai_service = AIService()
                        key_variable = await ai_service.question_ai_validation_check(
                            domain["domain_name"], 
                            question_data.question_text.strip().lower(),
                            all_questions_text.strip().lower()
                        )
                        
                        if isinstance(key_variable, list) and len(key_variable) > 0 and key_variable[0] not in ['0', 'Provide a relevant Question']:
                            update_data["question_lead"] = key_variable
            
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.db.questions.update_one(
                    {"_id": ObjectId(question_id)},
                    {"$set": update_data}
                )
                
                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail="Question not found")
            
            return {"message": "Question updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating question: {str(e)}")
    
    async def delete_question(self, question_id: str) -> Dict[str, str]:
        """Delete a question"""
        try:
            if not ObjectId.is_valid(question_id):
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            result = await self.db.questions.delete_one({"_id": ObjectId(question_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Also delete any results for this question
            await self.db.results.delete_many({"question_id": ObjectId(question_id)})
            
            return {"message": "Question deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting question: {str(e)}")
        

        