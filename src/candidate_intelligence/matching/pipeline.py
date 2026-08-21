"""Candidate matching pipeline orchestration."""

from __future__ import annotations

from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.matching.retrieval import CandidateRetriever
from candidate_intelligence.persistence.database.repositories.candidate_repo import (
    CandidateRepository,
)
from candidate_intelligence.persistence.database.repositories.match_repo import (
    MatchRepository,
)
from candidate_intelligence.scoring.evidence_scorer import EvidenceScorer
from candidate_intelligence.scoring.rules_scorer import RulesScorer


class MatchingPipeline:
    """Orchestrates candidate retrieval, scoring, ranking, and persistence."""

    def __init__(
        self,
        retriever: CandidateRetriever,
        candidate_repository: CandidateRepository,
        match_repository: MatchRepository,
        rules_scorer: RulesScorer,
        evidence_scorer: EvidenceScorer,
    ) -> None:
        self._retriever = retriever
        self._candidate_repository = candidate_repository
        self._match_repository = match_repository
        self._rules_scorer = rules_scorer
        self._evidence_scorer = evidence_scorer

    def match(
        self,
        job: JobDescription,
        limit: int = 10,
    ) -> list[MatchResult]:
        """Retrieve, score, rank, and persist candidate matches for a job."""
        retrieval_results = self._retriever.retrieve(job, limit=limit)

        matches: list[MatchResult] = []

        for retrieval_result in retrieval_results:
            candidate = self._candidate_repository.get(retrieval_result.candidate_id)

            if candidate is None:
                continue

            rules_score = self._rules_scorer.score(candidate, job)
            evidence_score = self._evidence_scorer.score(candidate, job)

            final_score = (rules_score + evidence_score) / 2

            matches.append(
                MatchResult(
                    job_id=job.job_id,
                    candidate_id=candidate.candidate_id,
                    rules_score=rules_score,
                    evidence_score=evidence_score,
                    final_score=final_score,
                )
            )

        ranked_matches = sorted(
            matches,
            key=lambda match: match.final_score or 0.0,
            reverse=True,
        )

        for rank, match in enumerate(ranked_matches, start=1):
            match.rank = rank
            self._match_repository.save(match)

        return ranked_matches
