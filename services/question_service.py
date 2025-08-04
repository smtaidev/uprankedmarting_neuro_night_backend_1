# services/question_service.py
from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

from api.models import Question, QuestionCreate, QuestionUpdate

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
                    "created_at": question["created_at"].isoformat()
                })
            
            return {"questions": result}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")
    
    async def add_question(self, domain_id: str, question_data: QuestionCreate) -> Dict[str, Any]:
        """Add a question to a domain"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            domain_obj_id = ObjectId(domain_id)
            
            # Check if domain exists
            domain = await self.db.domains.find_one({"_id": domain_obj_id})
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            # Create question
            question = Question(
                domain_id=domain_obj_id,
                question_text=question_data.question_text
            )
            
            question_dict = question.dict(by_alias=True)
            result = await self.db.questions.insert_one(question_dict)
            
            return {
                "id": str(result.inserted_id),
                "question_text": question_data.question_text,
                "message": "Question added successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding question: {str(e)}")
    
    async def update_question(self, question_id: str, question_data: QuestionUpdate) -> Dict[str, str]:
        """Update a question"""
        try:
            if not ObjectId.is_valid(question_id):
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            update_data = {}
            if question_data.question_text:
                update_data["question_text"] = question_data.question_text
            
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

