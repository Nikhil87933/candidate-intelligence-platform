"""Qdrant index for storing and searching candidate embeddings."""

from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


@dataclass(frozen=True)
class CandidateSearchResult:
    """A candidate match returned from vector search."""

    candidate_id: str
    score: float


class CandidateVectorIndex:
    """Handles storing and searching candidate embeddings in Qdrant."""

    def __init__(
        self, client: QdrantClient, collection_name: str, vector_size: int
    ) -> None:
        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if not self._client.collection_exists(self._collection_name):
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._vector_size, distance=Distance.COSINE
                ),
            )

    def upsert(self, candidate_id: str, vector: list[float]) -> None:
        """Insert or update a candidate's embedding vector."""
        self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=candidate_id,
                    vector=vector,
                    payload={"candidate_id": candidate_id},
                )
            ],
        )

    def search(
        self, query_vector: list[float], limit: int = 10
    ) -> list[CandidateSearchResult]:
        """Search for the most similar candidates to a query vector."""
        results = self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=limit,
        ).points

        return [
            CandidateSearchResult(
                candidate_id=str(point.payload["candidate_id"]),
                score=point.score,
            )
            for point in results
            if point.payload is not None
        ]
