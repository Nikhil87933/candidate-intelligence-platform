"""Tests for candidate semantic retrieval."""

from unittest.mock import MagicMock

from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.matching.retrieval import (
    CandidateRetrievalResult,
    CandidateRetriever,
)
from candidate_intelligence.vector.index import CandidateSearchResult


def test_retrieve_embeds_job_and_searches_candidates() -> None:
    """Verify retrieval embeds the job and searches the vector index."""
    embedder = MagicMock()
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_index = MagicMock()
    vector_index.search.return_value = [
        CandidateSearchResult(
            candidate_id="candidate-1",
            score=0.91,
        )
    ]

    retriever = CandidateRetriever(
        embedder=embedder,
        vector_index=vector_index,
    )

    job = JobDescription(
        job_id="job-1",
        title="Python Developer",
        required_skills=["Python", "FastAPI"],
        min_experience_years=3,
        summary="Build backend applications.",
    )

    results = retriever.retrieve(job, limit=5)

    embedder.embed.assert_called_once()
    vector_index.search.assert_called_once_with(
        query_vector=[0.1, 0.2, 0.3],
        limit=5,
    )

    assert results == [
        CandidateRetrievalResult(
            candidate_id="candidate-1",
            similarity_score=0.91,
        )
    ]


def test_build_query_text_includes_job_requirements() -> None:
    """Verify structured job requirements are included in embedding text."""
    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
        required_skills=["Python", "SQL", "Spark"],
        min_experience_years=4,
        responsibilities=["Build data pipelines"],
        qualifications=["Bachelor's degree"],
        summary="Design scalable data systems.",
    )

    query_text = CandidateRetriever._build_query_text(job)

    assert "Data Engineer" in query_text
    assert "Design scalable data systems." in query_text
    assert "Python, SQL, Spark" in query_text
    assert "Build data pipelines" in query_text
    assert "Bachelor's degree" in query_text
    assert "4 years" in query_text


def test_retrieve_returns_empty_list_when_no_candidates_found() -> None:
    """Verify retrieval handles an empty vector search result."""
    embedder = MagicMock()
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_index = MagicMock()
    vector_index.search.return_value = []

    retriever = CandidateRetriever(
        embedder=embedder,
        vector_index=vector_index,
    )

    job = JobDescription(
        job_id="job-1",
        title="Python Developer",
    )

    results = retriever.retrieve(job)

    assert results == []
