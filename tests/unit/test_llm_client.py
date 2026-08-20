"""Tests for the Ollama LLM client wrapper."""

from unittest.mock import MagicMock, patch

from candidate_intelligence.config.settings import Settings
from candidate_intelligence.llm.client import OllamaClient


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


def test_generate_json_returns_response_text() -> None:
    """Verify generate_json returns the response text from the Ollama client."""
    settings = _build_settings()

    with patch("candidate_intelligence.llm.client.ollama.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"response": '{"skills": []}'}
        mock_client_cls.return_value = mock_client

        client = OllamaClient(settings)
        result = client.generate_json("some prompt")

        assert result == '{"skills": []}'
        mock_client.generate.assert_called_once_with(
            model=settings.ollama_model,
            prompt="some prompt",
            format="json",
        )
