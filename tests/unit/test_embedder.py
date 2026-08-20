"""Tests for the Ollama embedder wrapper."""

from unittest.mock import MagicMock, patch

from candidate_intelligence.config.settings import Settings
from candidate_intelligence.embeddings.embedder import OllamaEmbedder


def _build_settings() -> Settings:
    return Settings(
        postgres_host="localhost",
        postgres_db="candidate_intelligence",
        postgres_user="candidate_user",
        postgres_password="candidate_password",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadmin123",
        qdrant_host="localhost",
    )


def test_embed_returns_embedding_vector() -> None:
    """Verify embed returns the embedding vector from the Ollama client."""
    settings = _build_settings()

    with patch("candidate_intelligence.embeddings.embedder.ollama.Client") as mock_cls:
        mock_client = MagicMock()
        mock_client.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_cls.return_value = mock_client

        embedder = OllamaEmbedder(settings)
        result = embedder.embed("some text")

        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.assert_called_once_with(
            model=settings.ollama_embedding_model, prompt="some text"
        )
