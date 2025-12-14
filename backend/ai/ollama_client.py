"""
Local Ollama Client for AI-driven infrastructure drift analysis.

This module provides an interface to a local Ollama instance running on
localhost:11434 for infrastructure analysis.

Architecture Notes:
-------------------
Ollama runs models locally, providing privacy and cost benefits. This client
connects to the Ollama API to run models like llama3, qwen2.5, or deepseek-r1
for infrastructure drift detection.

The Ollama API uses a simple REST interface:
POST http://localhost:11434/api/generate

This client is designed for full-file analysis, where the AI reads the entire
infrastructure configuration and returns structured drift analysis.

Future Extensions:
- Support for streaming responses
- Model selection based on file size/complexity
- Caching for repeated analyses
- Batch processing for multiple files
"""

import os
import json
import re
import httpx
from typing import Dict, List, Any, Optional


class LocalOllamaClient:
    """
    Client for interacting with local Ollama API.
    
    Connects to Ollama running on localhost:11434 and uses local models
    (llama3, qwen2.5, deepseek-r1) for infrastructure analysis.
    
    If Ollama is not running or model is unavailable, enters fallback mode.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: Optional[str] = None):
        """
        Initialize the Ollama client.
        
        Model Selection Priority:
        1. If model parameter is provided → use it
        2. Otherwise, use OLLAMA_MODEL from environment variable
        3. Fallback to "llama3:latest" if neither is set
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name to use (e.g., "llama3:latest", "wizardlm2:7b", "qwen2.5:7b")
                If None, will use OLLAMA_MODEL env var or default to "llama3:latest"
        """
        self.base_url = base_url.rstrip('/')
        # Model selection priority: requested model → env var → default
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3:latest")
        self.enabled = True  # Always enabled, will check availability on first call
        
        print(f"[Ollama] Initialized with model: {self.model}")
        if model:
            print(f"[Ollama] Model from parameter: {model}")
        elif os.getenv("OLLAMA_MODEL"):
            print(f"[Ollama] Model from OLLAMA_MODEL env var: {os.getenv('OLLAMA_MODEL')}")
        else:
            print(f"[Ollama] Using default model: llama3:latest")

    async def analyze_infrastructure(
        self,
        content: str,
        file_type: str,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Analyze entire infrastructure file using Ollama.
        
        This is the main method for AI-driven drift detection. It sends the
        entire file content to Ollama with a structured prompt requesting
        JSON output with drift_score, issues, and timeline.
        
        Args:
            content: Full infrastructure file content (Terraform/YAML/JSON/HCL)
            file_type: Type of infrastructure ("terraform" or "kubernetes")
            timeout: Request timeout in seconds (longer for local models)
        
        Returns:
            Dictionary with:
            - drift_score: float (0-100, will be normalized to 0-1)
            - issues: list of issue dictionaries
            - timeline: list of timeline event dictionaries
        
        On any error, returns empty structure for fallback.
        """
        try:
            print(f"[Ollama] Starting infrastructure analysis with model: {self.model}")
            print(f"[Ollama] File type: {file_type}")
            print(f"[Ollama] Content length: {len(content)} characters")
            
            # Build structured prompt for infrastructure analysis
            prompt = self._build_analysis_prompt(content, file_type)
            
            # Ollama API endpoint
            url = f"{self.base_url}/api/generate"
            
            # Ollama request format
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Request JSON output
            }
            
            print(f"[Ollama] Sending request to: {url}")
            print(f"[Ollama] Request payload model: {self.model}")
            print(f"[Ollama] Model source: {'parameter' if hasattr(self, '_model_source') else 'env/default'}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"[Ollama] Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text if hasattr(response, "text") else "Unknown error"
                print(f"[Ollama] ERROR: HTTP {response.status_code}")
                print(f"[Ollama] Full error response: {error_text}")
                
                # If 404, likely model doesn't exist - provide helpful message
                if response.status_code == 404:
                    print(f"[Ollama] Model '{self.model}' not found. Available models can be listed with: ollama list")
                    print(f"[Ollama] Common model names: llama3:latest, llama3:8b, llama3:70b, wizardlm2:latest, qwen2.5:latest")
                return self._empty_response()
            
            result = response.json()
            print(f"[Ollama] Raw API response received")
            print(f"[Ollama] Response keys: {list(result.keys())}")
            
            # Extract text from Ollama response
            # Format: {"response": "<text>", "done": true, ...}
            ai_text = result.get("response", "").strip()
            
            if not ai_text:
                print("[Ollama] Error: Empty response from Ollama")
                return self._empty_response()
            
            print(f"[Ollama] Parsed AI text (first 500 chars): {ai_text[:500]}...")
            
            # Parse JSON from AI response
            parsed = self._parse_json_response(ai_text)
            
            if not parsed:
                print("[Ollama] Error: Could not parse JSON from response")
                return self._empty_response()
            
            print("[Ollama] Successfully parsed JSON response")
            print(f"[Ollama] Drift score: {parsed.get('drift_score', 'N/A')}")
            print(f"[Ollama] Issues count: {len(parsed.get('issues', []))}")
            print(f"[Ollama] Timeline events: {len(parsed.get('timeline', []))}")
            
            # Normalize drift_score from 0-100 to 0-1
            if "drift_score" in parsed:
                drift_score = parsed["drift_score"]
                if isinstance(drift_score, (int, float)):
                    if drift_score > 1.0:  # Assume 0-100 scale
                        parsed["drift_score"] = min(drift_score / 100.0, 1.0)
                    parsed["drift_score"] = max(0.0, min(1.0, float(parsed["drift_score"])))
            
            return parsed
            
        except httpx.TimeoutException as e:
            print(f"[Ollama] Error: Request timeout: {e}")
            return self._empty_response()
        except httpx.RequestError as e:
            print(f"[Ollama] Error: Request failed: {e}")
            return self._empty_response()
        except Exception as e:
            print(f"[Ollama] Error: {e}")
            return self._empty_response()

    def _build_analysis_prompt(self, content: str, file_type: str) -> str:
        """
        Build structured prompt for infrastructure analysis.
        
        This prompt instructs the AI to analyze the entire infrastructure
        configuration and return structured JSON with drift analysis.
        
        Args:
            content: Infrastructure file content
            file_type: Type of infrastructure
        
        Returns:
            Formatted prompt string
        """
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
        
        AI models sometimes return JSON wrapped in markdown code blocks or
        with formatting issues. This method attempts to extract and repair
        the JSON.
        
        Repair strategies:
        1. Try direct JSON parsing
        2. Extract JSON from markdown code blocks (```json ... ```)
        3. Extract JSON object using regex
        4. Fix common JSON formatting issues
        
        Args:
            text: Raw text response from AI
        
        Returns:
            Parsed dictionary or None if parsing fails
        """
        # Strategy 1: Try direct JSON parsing
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
                # Validate it has expected structure
                if "drift_score" in parsed or "issues" in parsed:
                    print(f"[Ollama] Extracted JSON using regex (length: {len(candidate)})")
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # Strategy 4: Try to fix common issues
        # Remove markdown formatting
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        # Try to find the JSON object
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                candidate = cleaned[start_idx:end_idx+1]
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        print(f"[Ollama] JSON parsing failed. Text preview: {text[:200]}...")
        return None

    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response structure for fallback."""
        return {
            "drift_score": 0.0,
            "issues": [],
            "timeline": []
        }

