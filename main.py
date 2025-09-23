# main.py - UPDATED VERSION
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import os

from api.endpoints import router
from core.database import init_database, close_database
from services.embedding_service import global_embedding_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    try:
        # Initialize database first
        await init_database()
        
        # Initialize global embedding model
        logger.info("Initializing global embedding model...")
        global_embedding_service  # This will trigger model loading
        logger.info("Global embedding model initialized successfully")
        
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_database()

app = FastAPI(
    title="Production Call Center Q&A Processing API", 
    version="2.0.0",
    description="High-performance API for processing call center conversations",
    lifespan=lifespan
)

# Add middleware for production
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://localhost:3000/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API routes
app.include_router(router, prefix="")


@app.get("/")
async def read_root():
    return {
        "message": "Production Call Center Q&A Processing API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "POST /organizations/{org_id}/questions": "Add single question",
            "DELETE /organizations/{org_id}/questions/{question_id}": "Delete question",
            "PUT /organizations/{org_id}/questions/{question_id}": "Update question with validation",
            "GET /organizations/{org_id}/questions": "Get organization questions",
            "POST /organizations/{org_id}/conversations/upload": "Upload conversation file",
            "POST /organizations/{org_id}/conversations": "Process conversation (async)",
            "GET /organizations/{org_id}/conversations/{conv_id}/qa-pairs": "Get Q&A pairs",
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check including embedding model status"""
    try:
        from core.database import db
        if db.database:
            await db.database.command('ping')
            db_status = "healthy"
        else:
            db_status = "unhealthy"
    except:
        db_status = "unhealthy"
    
    # Check embedding model status
    try:
        model_status = "healthy" if global_embedding_service.model is not None else "unhealthy"
    except:
        model_status = "unhealthy"
    
    health_status = {
        "status": "healthy" if (db_status == "healthy" and model_status == "healthy") else "unhealthy",
        "database": db_status,
        "embedding_model": model_status,
        "uptime": time.time() - start_time
    }
    
    return health_status

# Store startup time
start_time = time.time()

if __name__ == "__main__":
    logger.info("Starting production server...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8500,
        workers=4,  # Multi-process for production
        reload=True,
        access_log=True
    )
