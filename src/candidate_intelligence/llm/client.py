"""LLM client wrapper for Ollama."""

from __future__ import annotations

import ollama

from candidate_intelligence.config.settings import Settings


class OllamaClient:
    """Thin wrapper around the Ollama client for structured JSON generation."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.ollama_model
        self._client = ollama.Client(host=settings.ollama_url)

    def generate_json(self, prompt: str) -> str:
        """Send a prompt to the model and return the raw JSON response text."""
        response = self._client.generate(
            model=self._model,
            prompt=prompt,
            format="json",
        )
        return str(response["response"])
