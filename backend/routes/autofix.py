"""
Auto-fix API routes for Cline integration.

This module provides REST API endpoints for:
- Generating patches for infrastructure issues
- Applying patches to workspace files

Endpoints:
- POST /autofix/generate: Generate a patch for an issue
- POST /autofix/apply: Apply a patch to a file
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from ai.cline_agent import get_cline_agent

router = APIRouter(prefix="/autofix", tags=["autofix"])


class GeneratePatchRequest(BaseModel):
    """Request model for patch generation."""
    issue: dict = Field(..., description="Issue dictionary with title, description, fix_suggestion, resource")
    file_content: str = Field(..., description="Current infrastructure file content (Terraform/YAML)")
    file_path: str = Field(default="infrastructure.tf", description="Path/filename for the infrastructure file")


class GeneratePatchResponse(BaseModel):
    """Response model for patch generation."""
    success: bool = Field(..., description="Whether patch generation was successful")
    diff: str = Field(..., description="Unified diff format patch, or error message if failed")
    message: str = Field(..., description="Human-readable status message")


class ApplyPatchRequest(BaseModel):
    """Request model for patch application."""
    diff: str = Field(..., description="Unified diff format patch to apply")
    target_file: str = Field(..., description="Path to the file to patch (relative to workspace)")
    workspace_path: Optional[str] = Field(default=None, description="Path to workspace root (optional)")


class ApplyPatchResponse(BaseModel):
    """Response model for patch application."""
    success: bool = Field(..., description="Whether patch was applied successfully")
    message: str = Field(..., description="Success message or error description")


@router.post("/generate", response_model=GeneratePatchResponse)
async def generate_patch(request: GeneratePatchRequest) -> GeneratePatchResponse:
    """
    Generate a patch for an infrastructure issue using Cline CLI.
    
    This endpoint:
    1. Takes issue information and current file content
    2. Uses Cline CLI to generate a fix
    3. Returns unified diff format patch
    
    Args:
        request: GeneratePatchRequest containing issue, file_content, and file_path
    
    Returns:
        GeneratePatchResponse with success status and diff
    
    Raises:
        HTTPException: If patch generation fails due to server error
    """
    try:
        agent = get_cline_agent()
        success, diff = agent.generate_patch(
            issue=request.issue,
            file_content=request.file_content,
            file_path=request.file_path
        )
        
        if success:
            return GeneratePatchResponse(
                success=True,
                diff=diff,
                message="Patch generated successfully"
            )
        else:
            return GeneratePatchResponse(
                success=False,
                diff="",
                message=diff  # diff contains error message in this case
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Patch generation failed: {str(e)}"
        )


@router.post("/apply", response_model=ApplyPatchResponse)
async def apply_patch(request: ApplyPatchRequest) -> ApplyPatchResponse:
    """
    Apply a unified diff patch to a target file.
    
    This endpoint:
    1. Takes a unified diff and target file path
    2. Applies the patch to the file in the workspace
    3. Returns success status
    
    Args:
        request: ApplyPatchRequest containing diff, target_file, and optional workspace_path
    
    Returns:
        ApplyPatchResponse with success status and message
    
    Raises:
        HTTPException: If patch application fails
    """
    try:
        agent = get_cline_agent()
        success, message = agent.apply_patch(
            diff=request.diff,
            target_file=request.target_file,
            workspace_path=request.workspace_path
        )
        
        return ApplyPatchResponse(
            success=success,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Patch application failed: {str(e)}"
        )

