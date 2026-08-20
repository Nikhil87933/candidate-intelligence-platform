"""Repository for match result persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.persistence.database.models import MatchModel


class MatchRepository:
    """Handles persistence of candidate-job match results."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, match: MatchResult) -> None:
        """Insert a new match result record."""
        model = MatchModel(
            job_id=match.job_id,
            candidate_id=match.candidate_id,
            rules_score=match.rules_score,
            evidence_score=match.evidence_score,
            final_score=match.final_score,
            rank=match.rank,
            rationale=match.rationale,
        )
        self._session.add(model)

    def get_for_job(self, job_id: str) -> list[MatchResult]:
        """Retrieve all match results for a given job, ordered by rank."""
        statement = (
            select(MatchModel)
            .where(MatchModel.job_id == job_id)
            .order_by(MatchModel.rank)
        )
        models = self._session.execute(statement).scalars().all()

        return [
            MatchResult(
                job_id=model.job_id,
                candidate_id=model.candidate_id,
                rules_score=model.rules_score,
                evidence_score=model.evidence_score,
                final_score=model.final_score,
                rank=model.rank,
                rationale=model.rationale,
            )
            for model in models
        ]
