"""Candidate retrieval using job embeddings and vector similarity search."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.embeddings.embedder import OllamaEmbedder
from candidate_intelligence.vector.index import (
    CandidateSearchResult,
    CandidateVectorIndex,
)


@dataclass(frozen=True)
class CandidateRetrievalResult:
    """A candidate returned by semantic retrieval."""

    candidate_id: str
    similarity_score: float


class CandidateRetriever:
    """Retrieves relevant candidates for a structured job description."""

    def __init__(
        self,
        embedder: OllamaEmbedder,
        vector_index: CandidateVectorIndex,
    ) -> None:
        self._embedder = embedder
        self._vector_index = vector_index

    def retrieve(
        self,
        job: JobDescription,
        limit: int = 10,
    ) -> list[CandidateRetrievalResult]:
        """Retrieve the most semantically relevant candidates for a job."""
        query_text = self._build_query_text(job)
        query_vector = self._embedder.embed(query_text)

        search_results = self._vector_index.search(
            query_vector=query_vector,
            limit=limit,
        )

        return [self._to_retrieval_result(result) for result in search_results]

    @staticmethod
    def _build_query_text(job: JobDescription) -> str:
        """Build embedding text from structured job requirements."""
        parts = [
            job.title or "",
            job.summary or "",
            "Required skills: " + ", ".join(job.required_skills),
            "Responsibilities: " + ", ".join(job.responsibilities),
            "Qualifications: " + ", ".join(job.qualifications),
        ]

        if job.min_experience_years is not None:
            parts.append(f"Minimum experience: {job.min_experience_years:g} years")

        return "\n".join(part for part in parts if part)

    @staticmethod
    def _to_retrieval_result(
        result: CandidateSearchResult,
    ) -> CandidateRetrievalResult:
        """Convert a vector search result into a retrieval result."""
        return CandidateRetrievalResult(
            candidate_id=result.candidate_id,
            similarity_score=result.score,
        )
