from pydantic import BaseModel, Field
from typing import Literal, Optional


class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="The Terraform or YAML text content")
    file_type: Literal["terraform", "kubernetes"] = Field(
        ..., description="Type of infrastructure file"
    )
    model: Optional[str] = Field(
        default=None,
        description="AI model to use (e.g., llama3:latest, wizardlm2:7b, qwen2.5:7b, deepseek-r1:8b, gemini-pro, oumi-rl). If None, backend uses OLLAMA_MODEL from .env for local models."
    )


class TimelineEvent(BaseModel):
    day: int = Field(..., description="Day number when the event occurred", ge=0)
    event: str = Field(..., description="Description of the event")
    severity: Literal["info", "low", "medium", "high"] = Field(
        ..., description="Severity level of the event"
    )


class Issue(BaseModel):
    id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Title of the issue")
    description: str = Field(..., description="Detailed description of the issue")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Severity level of the issue"
    )
    resource: str = Field(..., description="Resource name or identifier where the issue occurs")
    fix_suggestion: str = Field(..., description="Suggestion for fixing the issue")
    oumi_score: Optional[float] = Field(
        default=None,
        description="Oumi RL-based severity score (0.0-1.0). Higher values indicate more critical drift risk.",
        ge=0.0,
        le=1.0
    )


class AnalyzeResponse(BaseModel):
    drift_score: float = Field(
        ..., description="Drift score between 0 and 1", ge=0.0, le=1.0
    )
    timeline: list[TimelineEvent] = Field(
        ..., description="Timeline of events related to infrastructure changes"
    )
    issues: list[Issue] = Field(..., description="List of identified issues")
    provider: Optional[str] = Field(
        default=None,
        description="AI provider used (e.g., ollama, gemini, oumi, rule-engine)"
    )
    model: Optional[str] = Field(
        default=None,
        description="AI model used (e.g., llama3:latest, wizardlm2:7b, gemini-pro)"
    )
