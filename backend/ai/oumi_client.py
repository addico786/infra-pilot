"""
Oumi AI client for enhancing drift analysis with AI reasoning.

This module provides an interface to the Oumi AI API for:
- Generating detailed explanations for detected issues
- Creating actionable fix suggestions
- Predicting future drift timeline events
- Adjusting severity based on context

Architecture Notes:
-------------------
This file is intentionally structured for long-term maintainability.
All major steps (prompt building, API calls, parsing, fallbacks) are isolated
so future changes to Oumi API or InfraPilot can be implemented cleanly.

No patching. No inline hacks. Every component is modular and replaceable.
"""

import os
import json
import httpx
from typing import Dict, List, Any, Optional


class OumiClient:
    """
    Client for interacting with the Oumi AI API.

    If OUMI_API_KEY is missing, the client enters fallback mode,
    allowing InfraPilot to run without AI (useful for local testing).
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.oumi.ai/v1"):
        self.api_key = api_key or os.getenv("OUMI_API_KEY")
        self.base_url = base_url
        self.enabled = bool(self.api_key)

    # ===============================================================
    # ISSUE ANALYSIS (AI-enhanced)
    # ===============================================================
    async def analyze_issue(self, issue_data: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """
        Sends issue data to Oumi for AI-enhanced analysis.
        Returns enhanced fields such as explanation, fix suggestion, etc.
        """

        if not self.enabled:
            return self._fallback_issue_enhancement(issue_data)

        try:
            prompt = self._build_issue_analysis_prompt(issue_data)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "oumi:latest",
                        "messages": [
                            {"role": "system", "content": "You are an expert infrastructure drift analyst."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )

            if response.status_code != 200:
                return self._fallback_issue_enhancement(issue_data)

            result = response.json()

            # Oumi returns text — we expect the model to respond with JSON.
            ai_text = result["choices"][0]["message"]["content"].strip()

            parsed = json.loads(ai_text)

            return {
                "explanation": parsed.get("explanation", issue_data.get("description")),
                "fix_suggestion": parsed.get("fix_suggestion", "Review configuration."),
                "future_impact": parsed.get("future_impact", "Potential reliability or security drift."),
                "severity_adjustment": parsed.get("severity_adjustment")
            }

        except Exception as e:
            print(f"[Oumi Issue Analysis Error] {e}")
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
        """
        Sends base timeline + issues context to Oumi to generate
        a more realistic and informative drift timeline.
        """

        if not self.enabled:
            return timeline_events

        try:
            prompt = self._build_timeline_prompt(timeline_events, issues)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "oumi:latest",
                        "messages": [
                            {"role": "system", "content": "Enhance infrastructure drift timeline."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )

            if response.status_code != 200:
                return timeline_events

            result = response.json()
            ai_text = result["choices"][0]["message"]["content"].strip()
            parsed = json.loads(ai_text)

            if "timeline" in parsed and isinstance(parsed["timeline"], list):
                return parsed["timeline"]

            return timeline_events

        except Exception as e:
            print(f"[Oumi Timeline Error] {e}")
            return timeline_events

    # ===============================================================
    # FULL-FILE INFRASTRUCTURE ANALYSIS
    # ===============================================================
    async def analyze_infrastructure(
        self,
        content: str,
        file_type: str,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Analyze entire infrastructure file using Oumi.
        
        This method sends the full file content to Oumi with a structured
        prompt requesting JSON output with drift_score, issues, and timeline.
        
        Args:
            content: Full infrastructure file content (Terraform/YAML/JSON/HCL)
            file_type: Type of infrastructure ("terraform" or "kubernetes")
            timeout: Request timeout in seconds
        
        Returns:
            Dictionary with drift_score, issues, timeline, or empty structure if fails
        """
        if not self.enabled:
            return self._empty_infrastructure_response()
        
        try:
            print(f"[Oumi] Starting full-file infrastructure analysis")
            print(f"[Oumi] File type: {file_type}, Content length: {len(content)}")
            
            prompt = self._build_infrastructure_analysis_prompt(content, file_type)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "oumi:latest",
                        "messages": [
                            {"role": "system", "content": "You are an expert infrastructure drift analyst."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
            
            print(f"[Oumi] Infrastructure analysis response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text if hasattr(response, "text") else "Unknown error"
                print(f"[Oumi] Error: HTTP {response.status_code}: {error_text}")
                return self._empty_infrastructure_response()
            
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"].strip()
            
            print(f"[Oumi] Parsed AI text (first 500 chars): {ai_text[:500]}...")
            
            # Parse JSON with repair logic
            parsed = self._parse_json_response(ai_text)
            
            if not parsed:
                print("[Oumi] Error: Could not parse JSON from response")
                return self._empty_infrastructure_response()
            
            print("[Oumi] Successfully parsed infrastructure analysis JSON")
            print(f"[Oumi] Drift score: {parsed.get('drift_score', 'N/A')}")
            print(f"[Oumi] Issues count: {len(parsed.get('issues', []))}")
            print(f"[Oumi] Timeline events: {len(parsed.get('timeline', []))}")
            
            # Normalize drift_score from 0-100 to 0-1
            if "drift_score" in parsed:
                drift_score = parsed["drift_score"]
                if isinstance(drift_score, (int, float)):
                    if drift_score > 1.0:  # Assume 0-100 scale
                        parsed["drift_score"] = min(drift_score / 100.0, 1.0)
                    parsed["drift_score"] = max(0.0, min(1.0, float(parsed["drift_score"])))
            
            return parsed
            
        except Exception as e:
            print(f"[Oumi] Infrastructure analysis error: {e}")
            import traceback
            print(f"[Oumi] Traceback: {traceback.format_exc()}")
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
                    print(f"[Oumi] Extracted JSON using regex")
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
    # PROMPT BUILDERS
    # ===============================================================
    def _build_issue_analysis_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Builds the structured prompt sent to Oumi."""
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
        """Build structured prompt for timeline enhancement."""
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
    # FALLBACKS
    # ===============================================================
    def _fallback_issue_enhancement(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback results when AI is disabled or fails."""
        return {
            "explanation": issue_data.get("description", "Infrastructure issue detected."),
            "fix_suggestion": f"Review configuration for resource {issue_data.get('resource')}.",
            "future_impact": "May lead to operational or security problems.",
            "severity_adjustment": None
        }
