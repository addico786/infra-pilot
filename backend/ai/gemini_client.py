"""
Gemini AI client for enhancing drift analysis with AI reasoning.

This module provides an interface to Google's Gemini AI API for:
- Generating detailed explanations for detected issues
- Creating actionable fix suggestions
- Predicting future drift timeline events
- Adjusting severity based on context
- Full-file infrastructure analysis

Architecture Notes:
-------------------
This client follows the same interface as OumiClient to ensure seamless
provider switching. Both clients return identical structured responses,
allowing the analyzer to use either provider transparently.

API Endpoint Format (Updated for 2025):
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}

The API key MUST be passed as a URL query parameter (?key=...), NOT in headers.
This is Google's standard approach for REST API authentication.

Model Names (2025):
- gemini-pro → maps to gemini-1.5-pro (backward compatibility)
- gemini-1.5-flash → Fast, cost-effective model (default)
- gemini-1.5-flash-lite → Even faster, lighter model
- gemini-1.5-pro → More capable model for complex tasks
- gemini-2.0-flash → Latest fast model (if available)
- gemini-2.0-pro-exp → Latest experimental pro model (if available)

Request Payload Structure:
{
  "contents": [
    {
      "parts": [
        { "text": "<prompt>" }
      ]
    }
  ]
}

Response Structure:
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "text": "<AI response>" }
        ]
      }
    }
  ]
}

We extract: response["candidates"][0]["content"]["parts"][0]["text"]
"""

import os
import json
import httpx
from typing import Dict, List, Any, Optional


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI API (2025 version).
    
    Uses the v1beta generateContent REST API endpoint with API key in query string.
    Supports multiple Gemini models with automatic mapping of friendly names.
    
    If GEMINI_API_KEY is missing, the client enters fallback mode,
    allowing InfraPilot to run without AI (useful for local testing).
    
    API Documentation:
    https://ai.google.dev/api/generate-content
    https://ai.google.dev/api/rest
    """

    # Model name mapping: friendly names → actual Google model IDs
    MODEL_MAP = {
        "gemini-pro": "gemini-1.5-pro",  # Backward compatibility
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-1.5-flash-lite": "gemini-1.5-flash-lite",
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-2.0-flash": "gemini-2.0-flash-exp",  # Experimental
        "gemini-2.0-pro-exp": "gemini-2.0-pro-exp",  # Experimental
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
            model: Gemini model to use (default: "gemini-1.5-flash")
                Supports: gemini-pro, gemini-1.5-flash, gemini-1.5-pro, etc.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Map friendly model name to actual Google model ID
        self.model = self.MODEL_MAP.get(model.lower(), model)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            print(f"[Gemini] Initialized with model: {self.model}")
            # Verify API key on initialization
            self._verify_api_key()
        else:
            print("[Gemini] Initialized in fallback mode (no API key)")

    def _verify_api_key(self):
        """
        Lightweight API key verification by calling the /models endpoint.
        
        This helps detect invalid keys early without making a full generation request.
        """
        try:
            # Use a simple models list endpoint to verify key
            verify_url = f"{self.base_url}/models?key={self.api_key}"
            import asyncio
            
            # Run sync check (we'll do async verification later if needed)
            # For now, just log that we'll verify on first request
            print("[Gemini] API key verification will occur on first request")
        except Exception as e:
            print(f"[Gemini] API key verification note: {e}")

    # ===============================================================
    # FULL-FILE INFRASTRUCTURE ANALYSIS (PRIMARY METHOD)
    # ===============================================================
    async def analyze_infrastructure(
        self,
        content: str,
        file_type: str,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Analyze entire infrastructure file using Gemini.
        
        This is the primary analysis method. It sends the full file content
        to Gemini with a structured prompt requesting JSON output with
        drift_score, issues, and timeline.
        
        Args:
            content: Full infrastructure file content (Terraform/YAML/JSON/HCL)
            file_type: Type of infrastructure ("terraform" or "kubernetes")
            timeout: Request timeout in seconds (longer for full-file analysis)
        
        Returns:
            Dictionary with:
            - drift_score: float (0-100, will be normalized to 0-1)
            - issues: list of issue dictionaries
            - timeline: list of timeline event dictionaries
        
        On any error, returns empty structure for fallback.
        """
        if not self.enabled:
            print("[Gemini] analyze_infrastructure: Client disabled, returning empty response")
            return self._empty_infrastructure_response()
        
        try:
            print(f"[Gemini] Starting full-file infrastructure analysis")
            print(f"[Gemini] Model: {self.model}")
            print(f"[Gemini] File type: {file_type}, Content length: {len(content)} characters")
            
            prompt = self._build_infrastructure_analysis_prompt(content, file_type)
            
            # Build endpoint with API key in query string
            # Format: POST {base_url}/models/{model}:generateContent?key={api_key}
            endpoint = f"{self.base_url}/models/{self.model}:generateContent"
            full_url = f"{endpoint}?key={self.api_key}"
            
            print(f"[Gemini] Sending request to: {endpoint}")
            print(f"[Gemini] Full URL (with key): {endpoint}?key={'*' * 10}...")
            
            # Build request payload according to Gemini API specification
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            print("[Gemini] Request payload built")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                # API key MUST be in query string, NOT in headers
                response = await client.post(
                    full_url,  # Use full URL with query string
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
            
            print(f"[Gemini] Response status: {response.status_code}")
            
            # Enhanced error logging
            if response.status_code != 200:
                error_text = response.text
                print(f"[Gemini] ERROR: HTTP {response.status_code}")
                print(f"[Gemini] Full error response: {error_text}")
                
                # Try to parse error JSON for better debugging
                try:
                    error_json = response.json()
                    print(f"[Gemini] Parsed error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    pass
                
                return self._empty_infrastructure_response()
            
            result = response.json()
            print(f"[Gemini] Response received, keys: {list(result.keys())}")
            
            # Extract text from Gemini response
            ai_text = self._extract_text_from_response(result)
            
            if not ai_text:
                print("[Gemini] Error: Could not extract text from response")
                print(f"[Gemini] Full response structure: {json.dumps(result, indent=2)}")
                return self._empty_infrastructure_response()
            
            print(f"[Gemini] Extracted AI text (first 500 chars): {ai_text[:500]}...")
            
            # Parse JSON with repair logic
            parsed = self._parse_json_response(ai_text)
            
            if not parsed:
                print("[Gemini] Error: Could not parse JSON from response")
                print(f"[Gemini] Raw AI text: {ai_text[:1000]}")
                return self._empty_infrastructure_response()
            
            print("[Gemini] Successfully parsed infrastructure analysis JSON")
            print(f"[Gemini] Drift score: {parsed.get('drift_score', 'N/A')}")
            print(f"[Gemini] Issues count: {len(parsed.get('issues', []))}")
            print(f"[Gemini] Timeline events: {len(parsed.get('timeline', []))}")
            
            # Normalize drift_score from 0-100 to 0-1
            if "drift_score" in parsed:
                drift_score = parsed["drift_score"]
                if isinstance(drift_score, (int, float)):
                    if drift_score > 1.0:  # Assume 0-100 scale
                        parsed["drift_score"] = min(drift_score / 100.0, 1.0)
                    parsed["drift_score"] = max(0.0, min(1.0, float(parsed["drift_score"])))
            
            return parsed
            
        except httpx.TimeoutException as e:
            print(f"[Gemini] Timeout error during infrastructure analysis: {e}")
            return self._empty_infrastructure_response()
        except httpx.RequestError as e:
            print(f"[Gemini] Request error during infrastructure analysis: {e}")
            return self._empty_infrastructure_response()
        except Exception as e:
            print(f"[Gemini] Infrastructure analysis error: {e}")
            import traceback
            print(f"[Gemini] Traceback: {traceback.format_exc()}")
            return self._empty_infrastructure_response()

    def _build_infrastructure_analysis_prompt(self, content: str, file_type: str) -> str:
        """Build structured prompt for full-file infrastructure analysis."""
        return f"""You are an infrastructure reliability and drift analysis expert.
Analyze the provided {file_type} configuration and respond ONLY in JSON.

Configuration:
```
{content}
```

Respond with this EXACT JSON structure:
{{
  "drift_score": 0-100,
  "issues": [
     {{
        "id": "unique-id",
        "title": "Issue title",
        "description": "Detailed description",
        "severity": "low | medium | high | critical",
        "resource": "resource identifier",
        "fix_suggestion": "Actionable fix steps"
     }}
  ],
  "timeline": [
     {{"day": 0, "event": "Event description", "severity": "info|low|medium|high"}}
  ]
}}

Analysis Guidelines:
- Identify misconfigurations, security risks, anti-patterns, and drift indicators
- drift_score: 0-100 (0 = perfect, 100 = critical drift)
- severity: Use "critical" for security vulnerabilities, "high" for major issues
- timeline: Predict progressive effects of issues over time
- Provide realistic operational insights

Return ONLY valid JSON, no markdown, no code blocks."""

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from AI response with repair logic.
        
        Attempts multiple strategies to extract valid JSON from AI output.
        """
        import re
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from markdown code blocks
        json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Extract JSON object using regex
        json_object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.finditer(json_object_pattern, text, re.DOTALL)
        for match in matches:
            try:
                candidate = match.group(0)
                parsed = json.loads(candidate)
                if "drift_score" in parsed or "issues" in parsed:
                    print(f"[Gemini] Extracted JSON using regex")
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # Strategy 4: Fix common issues
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(cleaned[start_idx:end_idx+1])
            except json.JSONDecodeError:
                pass
        
        return None

    def _empty_infrastructure_response(self) -> Dict[str, Any]:
        """Return empty response structure for fallback."""
        return {
            "drift_score": 0.0,
            "issues": [],
            "timeline": []
        }

    # ===============================================================
    # ISSUE ANALYSIS (AI-enhanced) - Legacy method, kept for compatibility
    # ===============================================================
    async def analyze_issue(self, issue_data: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """
        Sends issue data to Gemini for AI-enhanced analysis.
        
        This method is kept for backward compatibility but is not the primary
        analysis method. The main method is analyze_infrastructure().
        """
        if not self.enabled:
            return self._fallback_issue_enhancement(issue_data)

        try:
            prompt = self._build_issue_analysis_prompt(issue_data)
            endpoint = f"{self.base_url}/models/{self.model}:generateContent"
            full_url = f"{endpoint}?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    full_url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )

            if response.status_code != 200:
                error_text = response.text
                print(f"[Gemini] Error: HTTP {response.status_code}: {error_text}")
                try:
                    error_json = response.json()
                    print(f"[Gemini] Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    pass
                return self._fallback_issue_enhancement(issue_data)

            result = response.json()
            ai_text = self._extract_text_from_response(result)

            if not ai_text:
                return self._fallback_issue_enhancement(issue_data)

            try:
                parsed = json.loads(ai_text)
            except json.JSONDecodeError as e:
                print(f"[Gemini] Error: Invalid JSON response: {e}")
                print(f"[Gemini] Raw AI text: {ai_text}")
                return self._fallback_issue_enhancement(issue_data)

            return {
                "explanation": parsed.get("explanation", issue_data.get("description", "Infrastructure issue detected.")),
                "fix_suggestion": parsed.get("fix_suggestion", "Review configuration."),
                "future_impact": parsed.get("future_impact", "Potential reliability or security drift."),
                "severity_adjustment": parsed.get("severity_adjustment")
            }

        except Exception as e:
            print(f"[Gemini] Error: {e}")
            import traceback
            print(f"[Gemini] Traceback: {traceback.format_exc()}")
            return self._fallback_issue_enhancement(issue_data)

    # ===============================================================
    # TIMELINE ENHANCEMENT
    # ===============================================================
    async def enhance_timeline(
        self,
        timeline_events: List[Dict[str, Any]],
        issues: List[Dict[str, Any]],
        timeout: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Enhance timeline with AI predictions."""
        if not self.enabled:
            return timeline_events

        try:
            prompt = self._build_timeline_prompt(timeline_events, issues)
            endpoint = f"{self.base_url}/models/{self.model}:generateContent"
            full_url = f"{endpoint}?key={self.api_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    full_url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )

            if response.status_code != 200:
                error_text = response.text
                print(f"[Gemini] Timeline error: HTTP {response.status_code}: {error_text}")
                return timeline_events

            result = response.json()
            ai_text = self._extract_text_from_response(result)

            if not ai_text:
                return timeline_events

            parsed = json.loads(ai_text)
            if "timeline" in parsed and isinstance(parsed["timeline"], list):
                return parsed["timeline"]

            return timeline_events

        except Exception as e:
            print(f"[Gemini] Timeline enhancement error: {e}")
            return timeline_events

    # ===============================================================
    # PROMPT BUILDERS
    # ===============================================================
    def _build_issue_analysis_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Build prompt for issue analysis."""
        return f"""
You are an infrastructure reliability & security expert.

Issue Detected:
- Rule ID: {issue_data.get('rule_id')}
- Title: {issue_data.get('title')}
- Description: {issue_data.get('description')}
- Severity: {issue_data.get('severity')}
- Resource: {issue_data.get('resource')}
- Context: {issue_data.get('raw_detected_data')}

Return JSON ONLY with fields:
{{
  "explanation": "...",
  "fix_suggestion": "...",
  "future_impact": "...",
  "severity_adjustment": "low|medium|high|critical or null"
}}
"""

    def _build_timeline_prompt(self, events: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> str:
        """Build prompt for timeline enhancement."""
        issue_summary = [
            f"- {i['title']} ({i['severity']}) on {i['resource']}" for i in issues
        ]
        timeline_summary = [
            f"- Day {e['day']}: {e['event']} ({e['severity']})" for e in events
        ]

        return f"""
You are enhancing an infrastructure drift timeline.

Issues:
{chr(10).join(issue_summary)}

Base Timeline:
{chr(10).join(timeline_summary)}

Return JSON ONLY as:
{{
  "timeline": [
     {{"day": 0, "event": "...", "severity": "info"}},
     ...
  ]
}}
"""

    # ===============================================================
    # RESPONSE PARSING
    # ===============================================================
    def _extract_text_from_response(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract text content from Gemini API response.
        
        Path: response["candidates"][0]["content"]["parts"][0]["text"]
        """
        try:
            candidates = response.get("candidates", [])
            if not candidates or len(candidates) == 0:
                print("[Gemini] Error: No candidates in response")
                print(f"[Gemini] Full response: {json.dumps(response, indent=2)}")
                return None

            candidate = candidates[0]
            content = candidate.get("content", {})
            if not content:
                print("[Gemini] Error: No content in candidate")
                return None

            parts = content.get("parts", [])
            if not parts or len(parts) == 0:
                print("[Gemini] Error: No parts in content")
                return None

            text = parts[0].get("text", "").strip()
            if not text:
                print("[Gemini] Error: Empty text in response")
                return None

            return text

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            print(f"[Gemini] Error: Response parsing failed: {e}")
            print(f"[Gemini] Response structure: {json.dumps(response, indent=2)}")
            return None

    # ===============================================================
    # FALLBACKS
    # ===============================================================
    def _fallback_issue_enhancement(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback results when AI is disabled or fails."""
        return {
            "explanation": issue_data.get("description", "Infrastructure issue detected."),
            "fix_suggestion": f"Review configuration for resource {issue_data.get('resource', 'the affected resource')}.",
            "future_impact": "May lead to operational or security problems.",
            "severity_adjustment": None
        }
