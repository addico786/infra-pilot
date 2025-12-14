"""
AI integration module for InfraPilot.

This module provides AI-powered enhancements to rule-based analysis,
including issue explanation, fix suggestions, and timeline generation.

Supported Providers:
- Oumi: Custom infrastructure-focused AI
- Gemini: Google's Gemini Pro model
- Ollama: Local models (llama3, qwen2.5, deepseek-r1)

Provider Selection:
The analyzer automatically selects a provider based on:
1. AI_PROVIDER environment variable (oumi | gemini | local)
2. Available API keys (OUMI_API_KEY, GEMINI_API_KEY)
3. Ollama availability (for local provider)
4. Fallback to rule-engine-only mode if no keys available
"""

from .oumi_client import OumiClient
from .gemini_client import GeminiClient
from .ollama_client import LocalOllamaClient

__all__ = ["OumiClient", "GeminiClient", "LocalOllamaClient"]
