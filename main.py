# main.py

import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from pathlib import Path
from api.endpoints import router
from core.config import settings
from core.database import init_database


logger = logging.getLogger(__name__)

app = FastAPI(title="Call Center RAG Application", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/scripts", StaticFiles(directory="frontend/scripts"), name="scripts")
templates = Jinja2Templates(directory="frontend/templates")

# Include API routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    try:
        logger.debug("Calling init_database...")
        await init_database()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    from core.database import close_database
    await close_database()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

    