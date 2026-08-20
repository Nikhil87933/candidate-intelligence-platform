"""Qdrant vector store client."""

from __future__ import annotations

from qdrant_client import QdrantClient

from candidate_intelligence.config.settings import Settings


def build_qdrant_client(settings: Settings) -> QdrantClient:
    """Create a configured Qdrant client from application settings."""
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
