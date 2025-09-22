# core/database.py

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

db = MongoDB()

async def get_database():
    if db.database is None:
        logger.error("Database not initialized")
        raise ValueError("Database not initialized")
    return db.database

async def init_database():
    """Initialize MongoDB connection, create collections, and create indexes"""
    logger.info(f"Attempting to connect to MongoDB with URI: {settings.MONGODB_URL}")
    logger.info(f"Database Name: {settings.DATABASE_NAME}")
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create collections explicitly
        collections = ['questions','qa_pairs']

        existing_collections = await db.database.list_collection_names()
        for collection_name in collections:
            if collection_name not in existing_collections:
                await db.database.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} already exists")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB or initialize database: {str(e)}", exc_info=True)
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Questions collection indexes  
        await db.database.questions.create_index([("org_id", 1)], background=True)
        await db.database.questions.create_index([("org_id", 1), ("question_text", "text")], background=True)
        await db.database.questions.create_index([("created_at", DESCENDING)], background=True)

        # QA pairs collection indexes
        await db.database.qa_pairs.create_index([("conv_id", 1)], background=True)
        await db.database.qa_pairs.create_index([("created_at", DESCENDING)], background=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}", exc_info=True)
        raise

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


