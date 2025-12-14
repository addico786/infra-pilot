"""
Main analyzer service orchestrating AI-driven drift detection.

This module is the central coordination point for drift analysis:
1. AI-driven analysis of entire infrastructure file (primary method)
2. Rule-based detection (fallback if AI fails)
3. Oumi RL-based scoring of issues
4. Timeline generation from AI predictions
5. Drift score calculation (AI can override)

Architecture:
- AI Layer (ai/): Primary analysis using Gemini, Oumi, or Ollama
- Rule Engine (services/rules/): Fallback detection using pattern matching
- Oumi RL (ai/oumi_trainer.py): Provides RL-based severity scoring
- This module: Orchestrates the pipeline

AI Provider Selection:
The analyzer supports multiple AI providers selected via AI_PROVIDER env var:
- "gemini": Uses GeminiClient (requires GEMINI_API_KEY)
- "oumi": Uses OumiClient (requires OUMI_API_KEY)
- "local": Uses LocalOllamaClient (requires Ollama running on localhost:11434)
- Fallback: If provider invalid or unavailable, tries other providers, then rule-engine

AI-Driven Analysis:
The primary analysis method sends the entire infrastructure file to the AI
with a structured prompt requesting JSON output. The AI identifies:
- Misconfigurations
- Security risks
- Anti-patterns
- Drift indicators

The AI returns structured output with drift_score, issues, and timeline.

Oumi RL Scoring:
After AI analysis, each issue is scored using the Oumi RL model.
This provides a 0-1 severity score based on reinforcement learning fine-tuning.

To extend:
- Add new file types: Update prompt builder
- Add new AI providers: Create client with analyze_infrastructure() method
- Modify drift score calculation: Update _calculate_drift_score()
"""

import os
import sys
import json
import re
import asyncio
from typing import List, Optional, Dict, Any

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from models import AnalyzeResponse, TimelineEvent, Issue
from services.rules import analyze_terraform, analyze_kubernetes


# Import AI clients - using Optional imports to handle missing dependencies gracefully
try:
    from ai.oumi_client import OumiClient
    OUMI_AVAILABLE = True
except ImportError:
    OumiClient = None
    OUMI_AVAILABLE = False

try:
    from ai.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GeminiClient = None
    GEMINI_AVAILABLE = False

try:
    from ai.ollama_client import LocalOllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    LocalOllamaClient = None
    OLLAMA_AVAILABLE = False

# Import Oumi RL scorer
try:
    from ai.oumi_trainer import score_issue_with_oumi
    OUMI_RL_AVAILABLE = True
except ImportError:
    OUMI_RL_AVAILABLE = False
    def score_issue_with_oumi(issue_data):
        # Fallback: rule-based scoring
        severity = issue_data.get('severity', 'medium').lower()
        severity_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 0.95}
        return severity_scores.get(severity, 0.5)


async def analyze_content(content: str, file_type: str, model: Optional[str] = None) -> AnalyzeResponse:
    """
    Main entry point for infrastructure content analysis.
    
    This function uses AI-first approach:
    1. Attempts AI-driven analysis of entire file
    2. Falls back to rule-based detection if AI fails
    3. Adds Oumi RL scoring to issues
    4. Returns structured AnalyzeResponse
    
    Args:
        content: Infrastructure configuration content (Terraform or Kubernetes YAML)
        file_type: Type of file ("terraform" or "kubernetes")
        model: Optional AI model name (e.g., llama3:latest, wizardlm2:7b, gemini-pro)
            If None, backend will use OLLAMA_MODEL from .env for local models
    
    Returns:
        AnalyzeResponse with drift score, timeline, enhanced issues, provider, and model info
    
    This function is async because AI analysis requires async API calls.
    """
    print("=" * 60)
    print("[Analyzer] Starting infrastructure analysis")
    print(f"[Analyzer] File type: {file_type}")
    print(f"[Analyzer] Content length: {len(content)} characters")
    if model:
        print(f"[Analyzer] Requested model: {model}")
    print("=" * 60)
    
    # Determine provider and model from request
    provider_name, model_name, client = _get_provider_and_model(model)
    
    # ---- AI-DRIVEN ANALYSIS (PRIMARY) ----
    # Attempt to get AI-driven analysis of entire file
    # If Gemini (or any AI) fails, we gracefully fall back to rule engine
    # This ensures analysis always completes, even if AI is unavailable
    try:
        ai_result = await _analyze_with_ai(content, file_type, client, model_name)
        
        if ai_result and ai_result.get("issues"):
            print("[Analyzer] AI analysis successful, using AI results")
            issues = ai_result.get("issues", [])
            timeline = ai_result.get("timeline", [])
            ai_drift_score = ai_result.get("drift_score", 0.0)
            
            # Normalize drift_score if needed (AI may return 0-100)
            if isinstance(ai_drift_score, (int, float)):
                if ai_drift_score > 1.0:
                    ai_drift_score = min(ai_drift_score / 100.0, 1.0)
                ai_drift_score = max(0.0, min(1.0, float(ai_drift_score)))
        else:
            print("[Analyzer] AI analysis failed or returned no issues, falling back to rule engine")
            # ---- RULE ENGINE FALLBACK ----
            raw_issues = _run_rule_engine(content, file_type)
            issues = _format_rule_engine_issues(raw_issues)
            timeline = _generate_timeline_skeleton(issues)
            ai_drift_score = None
            # Update provider/model for rule-engine fallback
            if not provider_name or provider_name == "rule-engine":
                provider_name = "rule-engine"
                model_name = None
    except Exception as e:
        # Catch any errors from AI analysis (e.g., Gemini API errors, network issues)
        # Fall back to rule engine to ensure analysis completes
        print(f"[Analyzer] AI analysis raised exception: {e}")
        print("[Analyzer] Falling back to rule engine")
        import traceback
        print(f"[Analyzer] Traceback: {traceback.format_exc()}")
        raw_issues = _run_rule_engine(content, file_type)
        issues = _format_rule_engine_issues(raw_issues)
        timeline = _generate_timeline_skeleton(issues)
        ai_drift_score = None
        provider_name = "rule-engine"
        model_name = None
    
    # ---- OUMI RL SCORING ----
    # Add Oumi RL-based severity scores to each issue
    # This uses reinforcement learning to provide more accurate severity assessment
    print("[Analyzer] Adding Oumi RL scores to issues")
    issues = _add_oumi_scores(issues)
    
    # ---- DRIFT SCORE CALCULATION ----
    # Use AI score if available, otherwise calculate from issues
    if ai_drift_score is not None:
        print(f"[Analyzer] Using AI-provided drift score: {ai_drift_score}")
        drift_score = ai_drift_score
    else:
        print("[Analyzer] Calculating drift score from issues")
        drift_score = _calculate_drift_score(issues)
    
    # Ensure drift_score is in valid range
    drift_score = max(0.0, min(1.0, float(drift_score)))
    
    # ---- FINAL RESPONSE ----
    # Convert data structures to Pydantic models
    timeline_events = [
        TimelineEvent(
            day=event.get("day", 0),
            event=event.get("event", ""),
            severity=_normalize_timeline_severity(event.get("severity", "info"))
        )
        for event in timeline
    ]
    
    issues_list = []
    for idx, issue in enumerate(issues, 1):
        # Ensure all required fields are present
        issue_id = issue.get("id") or f"issue-{idx:03d}"
        title = issue.get("title") or "Infrastructure Issue"
        description = issue.get("description") or issue.get("explanation", "")
        severity = _normalize_severity(issue.get("severity") or issue.get("final_severity", "medium"))
        resource = issue.get("resource") or "unknown"
        fix_suggestion = issue.get("fix_suggestion") or "Review and fix the configuration issue."
        oumi_score = issue.get("oumi_score")
        
        issues_list.append(
        Issue(
                id=issue_id,
                title=title,
                description=description,
                severity=severity,
                resource=resource,
                fix_suggestion=fix_suggestion,
                oumi_score=oumi_score
            )
        )
    
    print("=" * 60)
    print(f"[Analyzer] Analysis complete")
    print(f"[Analyzer] Drift score: {drift_score}")
    print(f"[Analyzer] Issues found: {len(issues_list)}")
    print(f"[Analyzer] Timeline events: {len(timeline_events)}")
    print("=" * 60)
    
    return AnalyzeResponse(
        drift_score=drift_score,
        timeline=timeline_events,
        issues=issues_list,
        provider=provider_name,
        model=model_name
    )


def _get_provider_and_model(requested_model: Optional[str] = None):
    """
    Determine AI provider and model based on requested model name.
    
    Model Selection Priority:
    1. If requested_model is provided → use it
    2. If no model provided → use OLLAMA_MODEL from .env (for local) or default provider
    
    Model mapping:
    - Any model starting with "llama3", "wizardlm2", "qwen2.5", "deepseek-r1" → ollama (local)
    - gemini-pro, gemini-1.5-flash, etc. → gemini (cloud)
    - oumi-rl → oumi (cloud, but only for scoring, not analysis)
    
    Args:
        requested_model: Model name from request (e.g., "llama3:latest", "wizardlm2:7b")
            If None, will use OLLAMA_MODEL from .env for local models
    
    Returns:
        Tuple of (provider_name, model_name, client_instance)
    """
    print(f"[Analyzer] _get_provider_and_model called with requested_model: {requested_model}")
    
    if not requested_model:
        # No model specified by UI - use environment-based selection
        print("[Analyzer] No model specified, using environment-based selection")
        print(f"[Analyzer] Checking OLLAMA_MODEL env var: {os.getenv('OLLAMA_MODEL', '(not set)')}")
        
        client = _get_ai_client()
        if client is None:
            print("[Analyzer] No AI client available, using rule-engine")
            return ("rule-engine", None, None)
        if OLLAMA_AVAILABLE and isinstance(client, LocalOllamaClient):
            print(f"[Analyzer] Using Ollama with model from env/default: {client.model}")
            return ("ollama", client.model, client)
        elif GEMINI_AVAILABLE and isinstance(client, GeminiClient):
            print(f"[Analyzer] Using Gemini with model: {client.model}")
            return ("gemini", client.model, client)
        elif OUMI_AVAILABLE and isinstance(client, OumiClient):
            print(f"[Analyzer] Using Oumi with model: oumi:latest")
            return ("oumi", "oumi:latest", client)
        else:
            print("[Analyzer] Unknown client type, using rule-engine")
            return ("rule-engine", None, None)
    
    # Map model names to providers
    model_lower = requested_model.lower()
    print(f"[Analyzer] Processing requested model: {requested_model} (lowercase: {model_lower})")
    
    # Ollama models (local) - check by prefix to support any version tag
    # Examples: llama3:latest, llama3:8b, llama3:70b, wizardlm2:7b, qwen2.5:14b, etc.
    ollama_prefixes = ["llama3", "wizardlm2", "qwen2.5", "deepseek-r1"]
    is_ollama_model = any(model_lower.startswith(prefix) for prefix in ollama_prefixes)
    
    if is_ollama_model:
        if OLLAMA_AVAILABLE:
            print(f"[Analyzer] Detected Ollama model: {requested_model}")
            # Pass the exact model name to LocalOllamaClient
            # It will use this, or fall back to OLLAMA_MODEL env var, or default to llama3:latest
            client = LocalOllamaClient(model=requested_model)
            print(f"[Analyzer] Created LocalOllamaClient with model: {client.model}")
            return ("ollama", client.model, client)
        else:
            print(f"[Analyzer] Requested Ollama model {requested_model} but Ollama not available")
            return ("rule-engine", None, None)
    
    # Gemini models (cloud)
    gemini_models = ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-flash-lite", 
                     "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-pro-exp"]
    if model_lower in gemini_models or model_lower.startswith("gemini"):
        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            # Map friendly model name to actual model
            # gemini-pro → gemini-1.5-pro for backward compatibility
            actual_model = requested_model if requested_model.lower() in gemini_models else "gemini-1.5-flash"
            client = GeminiClient(model=actual_model)
            return ("gemini", actual_model, client)
        else:
            print(f"[Analyzer] Requested Gemini model {requested_model} but Gemini not available or no API key")
            return ("rule-engine", None, None)
    
    # Oumi RL (scoring only, not for analysis)
    if model_lower == "oumi-rl":
        # Oumi RL is used for scoring, not analysis
        # Fall back to default AI provider for analysis
        client = _get_ai_client()
        if client:
            if OLLAMA_AVAILABLE and isinstance(client, LocalOllamaClient):
                return ("ollama", client.model, client)
            elif GEMINI_AVAILABLE and isinstance(client, GeminiClient):
                return ("gemini", "gemini-1.5-flash", client)
            elif OUMI_AVAILABLE and isinstance(client, OumiClient):
                return ("oumi", "oumi:latest", client)
        return ("rule-engine", None, None)
    
    # Unknown model
    print(f"[Analyzer] Unknown model: {requested_model}, falling back to default")
    client = _get_ai_client()
    if client:
        if OLLAMA_AVAILABLE and isinstance(client, LocalOllamaClient):
            return ("ollama", client.model, client)
        elif GEMINI_AVAILABLE and isinstance(client, GeminiClient):
            return ("gemini", "gemini-1.5-flash", client)
        elif OUMI_AVAILABLE and isinstance(client, OumiClient):
            return ("oumi", "oumi:latest", client)
    return ("rule-engine", None, None)


async def _analyze_with_ai(content: str, file_type: str, client: Optional[Any] = None, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Attempt AI-driven analysis of entire infrastructure file.
    
    This is the primary analysis method. It sends the full file content
    to the AI provider with a structured prompt requesting JSON output.
    
    The AI analyzes the entire configuration and returns:
    - drift_score: Overall drift assessment (0-100, normalized to 0-1)
    - issues: List of detected issues with full details
    - timeline: Predicted timeline of drift progression
    
    Args:
        content: Full infrastructure file content
        file_type: Type of infrastructure
        client: AI client instance (if None, will try to get one)
        model_name: Model name being used
    
    Returns:
        Dictionary with drift_score, issues, timeline, or None if AI fails
    """
    if client is None:
        client = _get_ai_client()
    
    if client is None:
        print("[Analyzer] No AI client available for analysis")
        return None
    
    try:
        # Check if client supports full-file analysis
        if hasattr(client, 'analyze_infrastructure'):
            print(f"[Analyzer] Using {client.__class__.__name__} for full-file analysis")
            result = await client.analyze_infrastructure(content, file_type)
            
            # Validate and normalize result
            if result and isinstance(result, dict):
                # Ensure issues is a list
                if "issues" not in result:
                    result["issues"] = []
                if not isinstance(result["issues"], list):
                    result["issues"] = []
                
                # Ensure timeline is a list
                if "timeline" not in result:
                    result["timeline"] = []
                if not isinstance(result["timeline"], list):
                    result["timeline"] = []
                
                # Normalize drift_score
                if "drift_score" in result:
                    score = result["drift_score"]
                    if isinstance(score, (int, float)):
                        if score > 1.0:  # Assume 0-100 scale
                            result["drift_score"] = min(score / 100.0, 1.0)
                        result["drift_score"] = max(0.0, min(1.0, float(result["drift_score"])))
                    else:
                        result["drift_score"] = 0.0
                else:
                    result["drift_score"] = 0.0
                
                return result
        
        # Fallback: If client doesn't support analyze_infrastructure, skip AI analysis
        print(f"[Analyzer] Client {client.__class__.__name__} does not support full-file analysis")
        return None
        
    except Exception as e:
        print(f"[Analyzer] AI analysis failed: {e}")
        import traceback
        print(f"[Analyzer] Traceback: {traceback.format_exc()}")
        return None


def _get_ai_client():
    """
    Get the appropriate AI client based on environment configuration.
    
    Provider Selection Logic (deterministic, in order):
    1. If AI_PROVIDER=gemini AND GEMINI_API_KEY exists → return GeminiClient()
    2. If AI_PROVIDER=oumi AND OUMI_API_KEY exists → return OumiClient()
    3. If AI_PROVIDER=local → return LocalOllamaClient() (check availability)
    4. If AI_PROVIDER not set/invalid AND GEMINI_API_KEY exists → return GeminiClient()
    5. If AI_PROVIDER not set/invalid AND OUMI_API_KEY exists → return OumiClient()
    6. If AI_PROVIDER not set/invalid → try LocalOllamaClient()
    7. Otherwise → return None (rule-engine-only mode)
    
    Returns:
        AI client instance (GeminiClient, OumiClient, LocalOllamaClient, or None)
    """
    # Get provider from env (case-insensitive)
    provider_raw = os.getenv("AI_PROVIDER", "").strip()
    provider = provider_raw.lower() if provider_raw else ""
    
    # Log loaded provider
    print(f"[AI Provider] Loaded AI_PROVIDER={provider_raw if provider_raw else '(not set)'}")
    
    # Check API keys availability
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    oumi_key = os.getenv("OUMI_API_KEY", "").strip()
    
    has_gemini_key = bool(gemini_key)
    has_oumi_key = bool(oumi_key)
    
    # Logic 1: AI_PROVIDER=gemini AND GEMINI_API_KEY exists
    if provider == "gemini":
        if GEMINI_AVAILABLE and has_gemini_key:
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            print(f"[AI Provider] Gemini selected. Using Gemini AI engine with model: {model}")
            return GeminiClient(model=model)
        else:
            if not GEMINI_AVAILABLE:
                print("[AI Provider] Gemini selected but GeminiClient not available. Checking fallbacks.")
            elif not has_gemini_key:
                print("[AI Provider] Gemini selected but GEMINI_API_KEY not found. Checking fallbacks.")
    
    # Logic 2: AI_PROVIDER=oumi AND OUMI_API_KEY exists
    if provider == "oumi":
        if OUMI_AVAILABLE and has_oumi_key:
            print("[AI Provider] Oumi selected. Using Oumi AI engine.")
            return OumiClient()
        else:
            if not OUMI_AVAILABLE:
                print("[AI Provider] Oumi selected but OumiClient not available. Checking fallbacks.")
            elif not has_oumi_key:
                print("[AI Provider] Oumi selected but OUMI_API_KEY not found. Checking fallbacks.")
    
    # Logic 3: AI_PROVIDER=local → try Ollama
    if provider == "local":
        if OLLAMA_AVAILABLE:
            # Use OLLAMA_MODEL from env, or default to llama3:latest
            model = os.getenv("OLLAMA_MODEL", "llama3:latest")
            print(f"[AI Provider] Local Ollama selected. Using model: {model}")
            print(f"[AI Provider] Model source: {'OLLAMA_MODEL env var' if os.getenv('OLLAMA_MODEL') else 'default (llama3:latest)'}")
            return LocalOllamaClient(model=model)
        else:
            print("[AI Provider] Local selected but LocalOllamaClient not available. Checking fallbacks.")
    
    # Logic 4: Provider not set/invalid, try Gemini if key exists
    if provider not in ["gemini", "oumi", "local"]:
        if GEMINI_AVAILABLE and has_gemini_key:
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            print(f"[AI Provider] No provider specified, but GEMINI_API_KEY found. Using Gemini AI engine with model: {model}")
            return GeminiClient(model=model)
    
    # Logic 5: Provider not set/invalid, try Oumi if key exists
    if provider not in ["gemini", "oumi", "local"]:
        if OUMI_AVAILABLE and has_oumi_key:
            print("[AI Provider] No provider specified, but OUMI_API_KEY found. Using Oumi AI engine.")
            return OumiClient()
    
    # Logic 6: Provider not set/invalid, try Ollama
    if provider not in ["gemini", "oumi", "local"]:
        if OLLAMA_AVAILABLE:
            # Use OLLAMA_MODEL from env, or default to llama3:latest
            model = os.getenv("OLLAMA_MODEL", "llama3:latest")
            print(f"[AI Provider] No provider specified, trying local Ollama with model: {model}")
            print(f"[AI Provider] Model source: {'OLLAMA_MODEL env var' if os.getenv('OLLAMA_MODEL') else 'default (llama3:latest)'}")
            return LocalOllamaClient(model=model)
    
    # Logic 7: No valid provider/key found
    print("[AI Provider] No valid AI provider configured. Using rule-engine-only mode.")
    return None


def _run_rule_engine(content: str, file_type: str) -> List[dict]:
    """
    Execute rule-based detection based on file type (FALLBACK ONLY).
    
    This is now used only as a fallback when AI analysis fails.
    
    Args:
        content: Configuration content
        file_type: Type of infrastructure ("terraform" or "kubernetes")
    
    Returns:
        List of raw issue dictionaries from rule engine
    """
    print("[Rule Engine] Running rule-based detection (fallback mode)")
    if file_type == "terraform":
        return analyze_terraform(content)
    elif file_type == "kubernetes":
        return analyze_kubernetes(content)
    else:
        return []


def _format_rule_engine_issues(raw_issues: List[dict]) -> List[dict]:
    """
    Format rule engine issues to match AI output structure.
    
    Converts rule engine output to the same format as AI analysis
    for consistent processing.
    
    Args:
        raw_issues: List of issue dictionaries from rule engine
    
    Returns:
        List of formatted issue dictionaries
    """
    formatted = []
    for idx, issue in enumerate(raw_issues, 1):
        formatted.append({
            "id": issue.get("rule_id") or f"rule-{idx:03d}",
            "title": issue.get("title", "Configuration Issue"),
            "description": issue.get("description", ""),
            "severity": issue.get("severity", "medium"),
            "resource": issue.get("resource", "unknown"),
            "fix_suggestion": "Review and fix the configuration issue."
        })
    return formatted


def _add_oumi_scores(issues: List[dict]) -> List[dict]:
    """
    Add Oumi RL-based severity scores to each issue.
    
    This function calls the Oumi RL scorer for each issue to get a
    reinforcement learning-based severity score (0-1). This score
    complements the AI/rule-based severity by learning from training examples.
    
    Args:
        issues: List of issue dictionaries (from AI or rule engine)
    
    Returns:
        List of issues with oumi_score field added
    """
    if not issues:
        return []
    
    scored_issues = []
    for issue in issues:
        try:
            # Get Oumi RL score for this issue
            oumi_score = score_issue_with_oumi(issue)
            issue["oumi_score"] = float(oumi_score)
        except Exception as e:
            # If scoring fails, use fallback (rule-based score)
            print(f"[Oumi RL] Scoring failed for issue {issue.get('title', 'unknown')}: {e}")
            severity = issue.get("severity", "medium").lower()
            severity_scores = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 0.95}
            issue["oumi_score"] = severity_scores.get(severity, 0.5)
        
        scored_issues.append(issue)
    
    return scored_issues


def _generate_timeline_skeleton(issues: List[dict]) -> List[dict]:
    """
    Generate a base timeline skeleton from detected issues (FALLBACK).
    
    Used when AI doesn't provide timeline. Creates a simple timeline
    based on issue severity and type.
    
    Args:
        issues: List of issue dictionaries
    
    Returns:
        List of timeline event dictionaries with day, event, severity
    """
    if not issues:
        return [
            {
                "day": 0,
                "event": "Infrastructure deployment completed successfully with no issues detected.",
                "severity": "info"
            }
        ]
    
    # Sort issues by severity (critical > high > medium > low)
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    sorted_issues = sorted(
        issues,
        key=lambda x: severity_order.get(x.get("severity", "medium"), 2),
        reverse=True
    )
    
    timeline = []
    
    # Day 0: Initial deployment
    timeline.append({
        "day": 0,
        "event": "Initial infrastructure deployment detected",
        "severity": "info"
    })
    
    # Add events for each issue, spacing them out
    days_per_severity = {"critical": 2, "high": 5, "medium": 10, "low": 15}
    
    current_day = 0
    for issue in sorted_issues[:5]:  # Limit to top 5 issues for timeline
        severity = issue.get("severity", "medium")
        day_offset = days_per_severity.get(severity, 10)
        current_day += day_offset
        
        issue_title = issue.get("title", "Configuration issue")
        resource = issue.get("resource", "resource")
        
        timeline.append({
            "day": current_day,
            "event": f"{issue_title} detected in {resource}",
            "severity": _map_severity_to_timeline(severity)
        })
    
    return timeline


def _map_severity_to_timeline(severity: str) -> str:
    """
    Map issue severity to timeline event severity.
    
    Timeline events use: info, low, medium, high
    Issues use: low, medium, high, critical
    """
    mapping = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "critical": "high"  # Map critical to high for timeline
    }
    return mapping.get(severity, "medium")


def _normalize_severity(severity: str) -> str:
    """Normalize severity to valid values."""
    valid = ["low", "medium", "high", "critical"]
    severity_lower = severity.lower()
    if severity_lower in valid:
        return severity_lower
    # Map common variations
    if severity_lower in ["info", "minor"]:
        return "low"
    if severity_lower in ["major", "severe"]:
        return "high"
    return "medium"


def _normalize_timeline_severity(severity: str) -> str:
    """Normalize timeline severity to valid values."""
    valid = ["info", "low", "medium", "high"]
    severity_lower = severity.lower()
    if severity_lower in valid:
        return severity_lower
    # Map common variations
    if severity_lower in ["warning", "warn"]:
        return "medium"
    if severity_lower in ["critical", "error"]:
        return "high"
    return "info"


def _calculate_drift_score(issues: List[dict]) -> float:
    """
    Calculate overall drift score based on detected issues.
    
    Drift score calculation:
    - If > 3 critical issues → 90+ (0.9+)
    - If many medium issues → 40-60 (0.4-0.6)
    - AI can override score (handled in analyze_content)
    
    Args:
        issues: List of enhanced issue dictionaries (with oumi_score)
    
    Returns:
        Drift score as float between 0.0 and 1.0
    """
    if not issues:
        return 0.0
    
    # Count issues by severity
    critical_count = sum(1 for issue in issues if issue.get("severity", "").lower() == "critical")
    high_count = sum(1 for issue in issues if issue.get("severity", "").lower() == "high")
    medium_count = sum(1 for issue in issues if issue.get("severity", "").lower() == "medium")
    low_count = sum(1 for issue in issues if issue.get("severity", "").lower() == "low")
    
    print(f"[Drift Score] Critical: {critical_count}, High: {high_count}, Medium: {medium_count}, Low: {low_count}")
    
    # Special case: > 3 critical issues → 90+ (0.9+)
    if critical_count > 3:
        score = 0.9 + (min(critical_count - 3, 7) * 0.01)  # 0.9 to 0.97
        print(f"[Drift Score] High critical count detected, score: {score}")
        return min(score, 1.0)
    
    # Weight issues by severity
    severity_weights = {
        "critical": 1.0,
        "high": 0.7,
        "medium": 0.4,
        "low": 0.2
    }
    
    total_weight = 0.0
    for issue in issues:
        # Prefer Oumi score if available, otherwise use severity-based weight
        if issue.get("oumi_score") is not None:
            weight = issue["oumi_score"]
        else:
            severity = issue.get("severity", "medium").lower()
            weight = severity_weights.get(severity, 0.4)
        total_weight += weight
    
    # Normalize to 0-1 range
    # Many medium issues → 40-60 (0.4-0.6)
    max_expected_weight = 10.0
    raw_score = min(total_weight / max_expected_weight, 1.0)
    
    # Apply curve for better distribution
    drift_score = min(raw_score ** 0.7, 1.0)
    
    # Ensure many medium issues fall in 0.4-0.6 range
    if medium_count >= 5 and critical_count == 0 and high_count == 0:
        drift_score = max(0.4, min(0.6, drift_score))
    
    print(f"[Drift Score] Calculated score: {drift_score}")
    return round(drift_score, 2)
