"""Match result domain model."""

from pydantic import BaseModel


class MatchResult(BaseModel):
    """A candidate-job match result produced by the matching pipeline."""

    job_id: str
    candidate_id: str
    rules_score: float | None = None
    evidence_score: float | None = None
    final_score: float | None = None
    rank: int | None = None
    rationale: str | None = None
