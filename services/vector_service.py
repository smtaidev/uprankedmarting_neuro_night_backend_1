# services/vector_service.py - FIXED VERSION WITH PROPER CHROMADB RESET
import chromadb
from chromadb.config import Settings as ChromaSettings
from services.embedding_service import global_embedding_service
from typing import List, Dict, Any
import logging
from core.config import settings
import os
import shutil
import re
import time
import gc

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize ChromaDB client"""
        try:
            os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            logger.info("Vector service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    def _reset_chromadb_client(self):
        """Reset ChromaDB client to release all file handles"""
        try:
            # Close current client if it exists
            if hasattr(self.client, 'reset') and callable(self.client.reset):
                self.client.reset()
            
            # Force garbage collection
            self.client = None
            gc.collect()
            
            # Wait for file handles to be released
            time.sleep(0.5)
            
            # Recreate client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            logger.info("ChromaDB client reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB client: {e}")
            # Fallback: recreate anyway
            try:
                self.client = chromadb.PersistentClient(
                    path=settings.CHROMADB_PATH,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            except Exception as fallback_error:
                logger.error(f"Fallback client creation failed: {fallback_error}")
    
    def create_collection(self, conversation_id: str) -> Any:
        """Create a new collection for a conversation"""
        try:
            if self.get_collection(conversation_id):
                return self.get_collection(conversation_id)
            
            collection_name = f"conversation_{conversation_id}"
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"conversation_id": conversation_id}
            )
            return collection
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def get_collection(self, conversation_id: str) -> Any:
        """Get existing collection for a conversation"""
        try:
            collection_name = f"conversation_{conversation_id}"
            return self.client.get_collection(collection_name)
        except Exception as e:
            logger.debug(f"Collection not found for {conversation_id}: {e}")
            return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation with proper ChromaDB reset"""
        try:
            collection_name = f"conversation_{conversation_id}"
            logger.info(f"Starting deletion for conversation: {conversation_id}")
            
            # Step 1: Delete ChromaDB collection
            collection_deleted = False
            try:
                collection = self.client.get_collection(collection_name)
                if collection:
                    self.client.delete_collection(collection_name)
                    collection_deleted = True
                    logger.info(f"Deleted ChromaDB collection: {collection_name}")
            except Exception as e:
                logger.debug(f"Collection {collection_name} not found: {e}")
            
            # Step 2: Check if any conversation collections remain
            remaining_collections = []
            try:
                all_collections = self.client.list_collections()
                remaining_collections = [c for c in all_collections if c.name.startswith("conversation_")]
                logger.info(f"Remaining conversation collections: {len(remaining_collections)}")
            except Exception as e:
                logger.error(f"Failed to list collections: {e}")
            
            # Step 3: If no conversation collections remain, clean up UUID folders
            if not remaining_collections:
                logger.info("No conversation collections remain, attempting UUID folder cleanup")
                
                # CRITICAL: Reset ChromaDB client to release file handles
                self._reset_chromadb_client()
                
                # Get UUID folders
                uuid_folders = self._get_uuid_folders()
                logger.info(f"Found {len(uuid_folders)} UUID folders to clean up")
                
                if uuid_folders:
                    success_count = 0
                    for uuid_folder in uuid_folders:
                        if self._delete_uuid_folder_force(uuid_folder):
                            success_count += 1
                    
                    logger.info(f"Successfully cleaned up {success_count}/{len(uuid_folders)} UUID folders")
                    return success_count > 0 or collection_deleted
            else:
                logger.info("Active conversation collections found, skipping UUID cleanup")
            
            return collection_deleted
            
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
    
    def _delete_uuid_folder_force(self, uuid_folder: str) -> bool:
        """Force delete UUID folder with multiple strategies"""
        folder_path = os.path.join(settings.CHROMADB_PATH, uuid_folder)
        
        if not os.path.exists(folder_path):
            logger.debug(f"Folder {uuid_folder} does not exist")
            return True
        
        # Strategy 1: Direct deletion
        try:
            shutil.rmtree(folder_path)
            logger.info(f"Successfully deleted UUID folder: {uuid_folder}")
            return True
        except PermissionError as e:
            logger.warning(f"Permission error on {uuid_folder}: {e}")
        except Exception as e:
            logger.warning(f"Direct deletion failed for {uuid_folder}: {e}")
        
        # Strategy 2: Try after a longer wait
        try:
            time.sleep(1.0)
            shutil.rmtree(folder_path)
            logger.info(f"Successfully deleted UUID folder on retry: {uuid_folder}")
            return True
        except Exception as e:
            logger.warning(f"Retry deletion failed for {uuid_folder}: {e}")
        
        # Strategy 3: Delete individual files first (Windows-specific approach)
        try:
            logger.info(f"Attempting individual file deletion for {uuid_folder}")
            
            # Delete files first
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.chmod(file_path, 0o777)  # Change permissions
                        os.remove(file_path)
                    except Exception as file_error:
                        logger.debug(f"Failed to delete file {file_path}: {file_error}")
                
                # Delete directories
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except Exception as dir_error:
                        logger.debug(f"Failed to delete directory {dir_path}: {dir_error}")
            
            # Finally remove the main folder
            os.rmdir(folder_path)
            logger.info(f"Successfully deleted UUID folder with individual file approach: {uuid_folder}")
            return True
            
        except Exception as e:
            logger.error(f"All deletion strategies failed for {uuid_folder}: {e}")
            return False
    
    def _get_uuid_folders(self) -> List[str]:
        """Get all UUID folders in vector_db directory"""
        try:
            uuid_folders = []
            if not os.path.exists(settings.CHROMADB_PATH):
                return uuid_folders
                
            for item in os.listdir(settings.CHROMADB_PATH):
                item_path = os.path.join(settings.CHROMADB_PATH, item)
                if os.path.isdir(item_path) and self._is_uuid_folder(item):
                    uuid_folders.append(item)
            return uuid_folders
        except Exception as e:
            logger.error(f"Failed to get UUID folders: {e}")
            return []
    
    def _is_uuid_folder(self, folder_name: str) -> bool:
        """Check if folder name matches UUID format"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, folder_name, re.IGNORECASE))
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks"""
        words = text.split()
        if not words:
            return [{"text": "", "chunk_id": "chunk_0", "start_index": 0, "end_index": 0}]
        
        chunk_size = max(settings.CHUNK_SIZE, 50)
        chunk_overlap = min(settings.CHUNK_OVERLAP, chunk_size // 2)
        chunks = []
        
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": f"chunk_{len(chunks)}",
                    "start_index": i,
                    "end_index": min(i + chunk_size, len(words))
                })
        
        return chunks if chunks else [{"text": text, "chunk_id": "chunk_0", "start_index": 0, "end_index": len(words)}]
    
    async def store_conversation(self, conversation_id: str, content: str):
        """Store conversation content"""
        try:
            if not content or not content.strip():
                logger.warning(f"Empty content for conversation {conversation_id}")
                return
            
            collection = self.create_collection(conversation_id)
            chunks = self.chunk_text(content)
            
            if not chunks:
                logger.warning(f"No chunks generated for conversation {conversation_id}")
                return
            
            # Generate embeddings and store
            texts = [chunk["text"] for chunk in chunks]
            embeddings = global_embedding_service.encode(texts).tolist()
            
            ids = [f"{conversation_id}_{chunk['chunk_id']}" for chunk in chunks]
            metadatas = [{
                "conversation_id": conversation_id,
                "chunk_id": chunk["chunk_id"],
                "start_index": chunk["start_index"],
                "end_index": chunk["end_index"]
            } for chunk in chunks]
            
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Stored {len(chunks)} chunks for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to store conversation {conversation_id}: {e}")
            raise
    
    async def search_similar(self, conversation_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            collection = self.get_collection(conversation_id)
            if not collection:
                logger.warning(f"No collection found for conversation {conversation_id}")
                return []
            
            count = collection.count()
            if count == 0:
                logger.warning(f"Empty collection for {conversation_id}")
                return []
            
            query_embedding = global_embedding_service.encode([query]).tolist()[0]
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, count),
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i]
                    similarity = max(0.0, 1 - distance)
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i],
                        "similarity": similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks for {conversation_id}: {e}")
            return []
    
    async def get_all_chunks(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all chunks as fallback"""
        try:
            collection = self.get_collection(conversation_id)
            if not collection or collection.count() == 0:
                return []
            
            results = collection.get(include=['documents', 'metadatas'])
            formatted_results = []
            
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][i],
                        "similarity": 0.5
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to get all chunks for {conversation_id}: {e}")
            return []