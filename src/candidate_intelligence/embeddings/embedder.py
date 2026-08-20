"""Text embedding generation using Ollama."""

from __future__ import annotations

import ollama

from candidate_intelligence.config.settings import Settings


class OllamaEmbedder:
    """Generates text embeddings using an Ollama embedding model."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.ollama_embedding_model
        self._client = ollama.Client(host=settings.ollama_url)

    def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        response = self._client.embeddings(model=self._model, prompt=text)
        return list(response["embedding"])
