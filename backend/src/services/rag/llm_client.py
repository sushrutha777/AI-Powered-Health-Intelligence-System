"""
LLM client abstraction layer.

Supports HuggingFace Inference API and OpenAI API through a
common interface for pluggable LLM backends.
"""

from abc import ABC, abstractmethod

import httpx

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class BaseLLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text from a prompt."""
        ...


class HuggingFaceLLMClient(BaseLLMClient):
    """HuggingFace Inference API client."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.model_name = settings.LLM_MODEL_NAME
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.3,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False,
            },
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    return str(result[0].get("generated_text", "")).strip()
                return str(result)

            except httpx.HTTPStatusError as e:
                logger.error("llm_api_error", status=e.response.status_code,
                             detail=e.response.text[:200])
                return (
                    "I apologize, but I'm unable to process your request right now. "
                    "Please try again."
                )
            except Exception as e:
                logger.error("llm_generation_error", error=str(e))
                return "An error occurred while generating the response."


class OpenAILLMClient(BaseLLMClient):
    """OpenAI API client (pluggable alternative)."""

    def __init__(self, api_key: str, model: str = "gpt-4") -> None:
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a knowledgeable medical AI assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return str(result["choices"][0]["message"]["content"]).strip()
            except Exception as e:
                logger.error("openai_generation_error", error=str(e))
                return "An error occurred while generating the response."


def get_llm_client() -> BaseLLMClient:
    """Factory function — returns the configured LLM client."""
    settings = get_settings()
    if settings.HUGGINGFACE_API_KEY:
        return HuggingFaceLLMClient()
    logger.warning("no_llm_api_key_configured")
    return HuggingFaceLLMClient()  # Will fail gracefully on generation
