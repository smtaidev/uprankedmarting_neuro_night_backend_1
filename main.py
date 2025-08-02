
# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import uvicorn
import os
from pathlib import Path

from api.endpoints import router
from core.config import settings

app = FastAPI(title="Call Center RAG Application", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
Path("uploads").mkdir(exist_ok=True)
Path("frontend/templates").mkdir(parents=True, exist_ok=True)
Path("frontend/css").mkdir(parents=True, exist_ok=True)
Path("frontend/scripts").mkdir(parents=True, exist_ok=True)

# Static files and templates
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/scripts", StaticFiles(directory="frontend/scripts"), name="scripts")
templates = Jinja2Templates(directory="frontend/templates")

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


    