from dotenv import load_dotenv
load_dotenv()

import os
import sys

# Ensure backend directory is in Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse
from services.analyzer import analyze_content
from services.emailer import (
    build_analysis_email_body,
    build_analysis_email_html,
    email_enabled,
    send_analysis_email,
)
from routes.autofix import router as autofix_router
from routes.auth import router as auth_router
from database import init_db

# Initialize database tables
init_db()

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
app.include_router(auth_router)


@app.get("/")
async def root() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "ok", "service": "infrapilot-backend"}
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks) -> AnalyzeResponse:
    """
    Analyze infrastructure content for drift and issues.
    
    Args:
        request: AnalyzeRequest containing content, file_type, and optional model
    
    Returns:
        AnalyzeResponse with drift score, timeline, issues, provider, and model info
    """
    response = await analyze_content(request.content, request.file_type, request.model)

    # Optional best-effort email delivery (feature-flagged, non-blocking)
    try:
        if email_enabled() and request.email:
            drift_percentage = round(max(0.0, min(1.0, response.drift_score)) * 100)
            subject = f"InfraPilot results (drift: {drift_percentage}%)"
            body = build_analysis_email_body(
                drift_score=response.drift_score,
                provider=response.provider,
                model=response.model,
                issues=response.issues,
                timeline=response.timeline,
            )
            html_body = build_analysis_email_html(
                drift_score=response.drift_score,
                provider=response.provider,
                model=response.model,
                issues=response.issues,
                timeline=response.timeline,
            )
            background_tasks.add_task(
                _send_email_background,
                to_email=request.email,
                subject=subject,
                body=body,
                html_body=html_body,
            )
    except Exception as e:
        # Never disrupt analysis response due to email errors
        print(f"[Email] Skipping email send due to error: {e}")

    return response


def _send_email_background(*, to_email: str, subject: str, body: str, html_body: str) -> None:
    try:
        send_analysis_email(to_email=to_email, subject=subject, body=body, html_body=html_body)
        print(f"[Email] Sent analysis email to {to_email}")
    except Exception as e:
        print(f"[Email] Failed to send analysis email to {to_email}: {e}")
