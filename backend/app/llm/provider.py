"""
LLM Provider abstraction.
Supports Ollama (local) with graceful fallback detection.
"""
import httpx
import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider:
    """Ollama local LLM provider."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check if our model (or any variant) is available
                model_name = self.model.split(":")[0]
                return any(model_name in m for m in models)
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            return False

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using Ollama."""
        payload = {
            "model": self.model,
            "prompt": f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1500,
            }
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")


class LLMProvider:
    """
    Unified LLM provider. Uses Ollama when available.
    Reports availability status accurately.
    """

    def __init__(self):
        self._ollama = OllamaProvider()
        self._available: Optional[bool] = None

    async def is_available(self) -> bool:
        available = await self._ollama.is_available()
        self._available = available
        return available

    async def generate(self, system_prompt: str, user_prompt: str) -> tuple[str, bool]:
        """
        Returns (response_text, is_real_llm).
        is_real_llm=False means fallback was used.
        """
        if await self.is_available():
            try:
                text = await self._ollama.generate(system_prompt, user_prompt)
                return text, True
            except Exception as e:
                logger.warning(f"Ollama generation failed: {e}")

        return "", False

    async def get_model_name(self) -> str:
        if await self.is_available():
            return self.model
        return "demo-mode"

    @property
    def model(self) -> str:
        return self._ollama.model
