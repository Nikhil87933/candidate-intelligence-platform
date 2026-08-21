"""Candidate matching API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from candidate_intelligence.api.schemas import (
    MatchResultsResponse,
    MatchRunRequest,
)
from candidate_intelligence.config.settings import Settings
from candidate_intelligence.embeddings.embedder import OllamaEmbedder
from candidate_intelligence.llm.client import OllamaClient
from candidate_intelligence.matching.pipeline import MatchingPipeline
from candidate_intelligence.matching.retrieval import CandidateRetriever
from candidate_intelligence.persistence.database.db import (
    build_engine,
    build_session_factory,
    session_scope,
)
from candidate_intelligence.persistence.database.repositories.candidate_repo import (
    CandidateRepository,
)
from candidate_intelligence.persistence.database.repositories.job_repo import (
    JobRepository,
)
from candidate_intelligence.persistence.database.repositories.match_repo import (
    MatchRepository,
)
from candidate_intelligence.ranking.llm_ranker import LLMFinalRanker
from candidate_intelligence.scoring.evidence_scorer import EvidenceScorer
from candidate_intelligence.scoring.rules_scorer import RulesScorer
from candidate_intelligence.vector.client import build_qdrant_client
from candidate_intelligence.vector.index import CandidateVectorIndex

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/{job_id}", response_model=MatchResultsResponse)
def run_matching(
    job_id: str,
    request: MatchRunRequest,
) -> MatchResultsResponse:
    """Run candidate retrieval, scoring, and final LLM ranking."""
    settings = Settings()

    engine = build_engine(settings)
    session_factory = build_session_factory(engine)

    with session_scope(session_factory) as session:
        candidate_repository = CandidateRepository(session)
        job_repository = JobRepository(session)
        match_repository = MatchRepository(session)

        job = job_repository.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}",
            )

        embedder = OllamaEmbedder(settings)
        qdrant_client = build_qdrant_client(settings)

        vector_index = CandidateVectorIndex(
            client=qdrant_client,
            collection_name=settings.qdrant_collection_candidates,
            vector_size=settings.embedding_vector_size,
        )

        retriever = CandidateRetriever(
            embedder=embedder,
            vector_index=vector_index,
        )

        pipeline = MatchingPipeline(
            retriever=retriever,
            candidate_repository=candidate_repository,
            match_repository=match_repository,
            rules_scorer=RulesScorer(),
            evidence_scorer=EvidenceScorer(),
        )

        matches = pipeline.match(
            job=job,
            limit=request.limit,
        )

        candidates = []
        for match in matches:
            candidate = candidate_repository.get(match.candidate_id)
            if candidate is not None:
                candidates.append(candidate)

        ranker = LLMFinalRanker(OllamaClient(settings))

        ranked_matches = ranker.rank(
            job=job,
            candidates=candidates,
            matches=matches,
        )

        for match in ranked_matches:
            match_repository.save(match)

    return MatchResultsResponse(matches=ranked_matches)


@router.get("/{job_id}", response_model=MatchResultsResponse)
def get_matches(job_id: str) -> MatchResultsResponse:
    """Return persisted match results for a job."""
    settings = Settings()

    engine = build_engine(settings)
    session_factory = build_session_factory(engine)

    with session_scope(session_factory) as session:
        match_repository = MatchRepository(session)
        matches = match_repository.get_for_job(job_id)

    return MatchResultsResponse(matches=matches)
