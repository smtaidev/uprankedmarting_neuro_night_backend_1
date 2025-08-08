# services/domain_service.py
from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

from api.models import Domain, DomainCreate, Question, QuestionCreate
from core.database import get_database
from services.question_service import QuestionService

class DomainService:
    def __init__(self, db):
        self.db = db
    
    async def create_domain(self, domain_data: DomainCreate) -> Dict[str, Any]:
        """Create a new domain with optional initial questions"""
        try:
            # Create domain
            domain = Domain(domain_name=domain_data.domain_name)
            domain_dict = domain.dict(by_alias=True)
            result = await self.db.domains.insert_one(domain_dict)
            domain_id = result.inserted_id
            
            # Add initial questions if provided
            questions_added = []
            if domain_data.questions:
                for question_text in domain_data.questions:
                    question = Question(
                        domain_id=domain_id,
                        question_text=question_text.strip()
                    )
                    question_dict = question.dict(by_alias=True)
                    
                    q_result = await self.db.questions.insert_one(question_dict)
                    questions_added.append({
                        "id": str(q_result.inserted_id),
                        "text": question_text.strip()
                    })
            
            return {
                "domain_id": str(domain_id),
                "domain_name": domain_data.domain_name,
                "questions_added": len(questions_added),
                "questions": questions_added,
                "message": "Domain created successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating domain: {str(e)}")
    
    async def get_all_domains(self) -> Dict[str, Any]:
        """Get all domains"""
        try:
            domains_cursor = self.db.domains.find().sort("created_at", -1)
            domains = await domains_cursor.to_list(length=None)
            
            # Convert ObjectId to string and add question count
            result = []
            for domain in domains:
                question_count = await self.db.questions.count_documents({"domain_id": domain["_id"]})
                result.append({
                    "id": str(domain["_id"]),
                    "domain_name": domain["domain_name"],
                    "question_count": question_count,
                    "created_at": domain["created_at"].isoformat()
                })
            
            return {"domains": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching domains: {str(e)}")
    
    async def delete_domain(self, domain_id: str) -> Dict[str, str]:
        """Delete domain and all associated data"""
        try:
            if not ObjectId.is_valid(domain_id):
                raise HTTPException(status_code=400, detail="Invalid domain ID")
            
            domain_obj_id = ObjectId(domain_id)
            
            # Check if domain exists
            domain = await self.db.domains.find_one({"_id": domain_obj_id})
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            # Delete associated questions
            await self.db.questions.delete_many({"domain_id": domain_obj_id})
            
            # Delete associated conversations and results
            conversations = await self.db.conversations.find({"domain_id": domain_obj_id}).to_list(length=None)
            for conv in conversations:
                await self.db.results.delete_many({"conversation_id": conv["_id"]})
            await self.db.conversations.delete_many({"domain_id": domain_obj_id})
            
            # Delete domain
            await self.db.domains.delete_one({"_id": domain_obj_id})
            
            return {"message": "Domain and all associated data deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting domain: {str(e)}")
    


