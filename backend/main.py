from dotenv import load_dotenv
load_dotenv()

import os
import sys

# Ensure backend directory is in Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse
from services.analyzer import analyze_content
from routes.autofix import router as autofix_router

app = FastAPI(
    title="InfraPilot Backend",
    description="Backend API for infrastructure analysis and drift detection",
    version="1.0.0"
)

# ---------------------------
# CORS CONFIGURATION (Required for Frontend → Backend Communication)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],          # Allow all headers
)

# ---------------------------
# ROUTERS
# ---------------------------
app.include_router(autofix_router)


@app.get("/")
async def root() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "ok", "service": "infrapilot-backend"}
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze infrastructure content for drift and issues.
    
    Args:
        request: AnalyzeRequest containing content, file_type, and optional model
    
    Returns:
        AnalyzeResponse with drift score, timeline, issues, provider, and model info
    """
    response = await analyze_content(request.content, request.file_type, request.model)
    return response
