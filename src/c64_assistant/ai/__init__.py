"""Modulo AI: Orchestrazione LLM, prompt engineering di dominio e guardrail deterministici."""

from .engine import AssistantEngine, AssistantResponse
from .llm_client import (
    BaseLLMClient,
    GeminiClient,
    OfflineClient,
    OllamaClient,
    OpenAIClient,
    get_llm_client,
)
from .prompts import (
    AUTO_FIX_PROMPT_TEMPLATE,
    RAG_PROMPT_TEMPLATE,
    SYSTEM_PROMPT_C64_EXPERT,
)

__all__ = [
    "AssistantEngine",
    "AssistantResponse",
    "BaseLLMClient",
    "OllamaClient",
    "GeminiClient",
    "OpenAIClient",
    "OfflineClient",
    "get_llm_client",
    "SYSTEM_PROMPT_C64_EXPERT",
    "RAG_PROMPT_TEMPLATE",
    "AUTO_FIX_PROMPT_TEMPLATE",
]
