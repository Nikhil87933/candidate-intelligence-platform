"""Tests for the candidate matching pipeline."""

from unittest.mock import MagicMock

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.matching.pipeline import MatchingPipeline
from candidate_intelligence.matching.retrieval import CandidateRetrievalResult


def test_pipeline_retrieves_scores_ranks_and_saves_matches() -> None:
    """Verify the pipeline orchestrates the complete deterministic flow."""
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        CandidateRetrievalResult(
            candidate_id="candidate-1",
            similarity_score=0.91,
        ),
        CandidateRetrievalResult(
            candidate_id="candidate-2",
            similarity_score=0.85,
        ),
    ]

    candidate_repository = MagicMock()
    candidate_repository.get.side_effect = [
        Candidate(
            candidate_id="candidate-1",
            skills=["Python", "SQL"],
            total_experience_years=5,
        ),
        Candidate(
            candidate_id="candidate-2",
            skills=["Python"],
            total_experience_years=3,
        ),
    ]

    match_repository = MagicMock()

    rules_scorer = MagicMock()
    rules_scorer.score.side_effect = [90.0, 60.0]

    evidence_scorer = MagicMock()
    evidence_scorer.score.side_effect = [80.0, 40.0]

    pipeline = MatchingPipeline(
        retriever=retriever,
        candidate_repository=candidate_repository,
        match_repository=match_repository,
        rules_scorer=rules_scorer,
        evidence_scorer=evidence_scorer,
    )

    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
        required_skills=["Python", "SQL"],
        min_experience_years=4,
    )

    results = pipeline.match(job, limit=5)

    retriever.retrieve.assert_called_once_with(job, limit=5)
    assert len(results) == 2

    assert results[0].candidate_id == "candidate-1"
    assert results[0].rules_score == 90.0
    assert results[0].evidence_score == 80.0
    assert results[0].final_score == 85.0
    assert results[0].rank == 1

    assert results[1].candidate_id == "candidate-2"
    assert results[1].rules_score == 60.0
    assert results[1].evidence_score == 40.0
    assert results[1].final_score == 50.0
    assert results[1].rank == 2

    assert match_repository.save.call_count == 2


def test_pipeline_skips_retrieved_candidate_missing_from_database() -> None:
    """Verify missing candidate records are skipped safely."""
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        CandidateRetrievalResult(
            candidate_id="missing-candidate",
            similarity_score=0.91,
        )
    ]

    candidate_repository = MagicMock()
    candidate_repository.get.return_value = None

    match_repository = MagicMock()
    rules_scorer = MagicMock()
    evidence_scorer = MagicMock()

    pipeline = MatchingPipeline(
        retriever=retriever,
        candidate_repository=candidate_repository,
        match_repository=match_repository,
        rules_scorer=rules_scorer,
        evidence_scorer=evidence_scorer,
    )

    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
    )

    results = pipeline.match(job)

    assert results == []
    rules_scorer.score.assert_not_called()
    evidence_scorer.score.assert_not_called()
    match_repository.save.assert_not_called()


def test_pipeline_returns_empty_list_when_retrieval_finds_nothing() -> None:
    """Verify the pipeline handles an empty retrieval result."""
    retriever = MagicMock()
    retriever.retrieve.return_value = []

    candidate_repository = MagicMock()
    match_repository = MagicMock()
    rules_scorer = MagicMock()
    evidence_scorer = MagicMock()

    pipeline = MatchingPipeline(
        retriever=retriever,
        candidate_repository=candidate_repository,
        match_repository=match_repository,
        rules_scorer=rules_scorer,
        evidence_scorer=evidence_scorer,
    )

    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
    )

    results = pipeline.match(job)

    assert results == []
    candidate_repository.get.assert_not_called()
    match_repository.save.assert_not_called()


def test_pipeline_ranks_candidates_by_final_score() -> None:
    """Verify candidates are ranked by final score, not retrieval order."""
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        CandidateRetrievalResult(
            candidate_id="candidate-low",
            similarity_score=0.95,
        ),
        CandidateRetrievalResult(
            candidate_id="candidate-high",
            similarity_score=0.80,
        ),
    ]

    candidate_repository = MagicMock()
    candidate_repository.get.side_effect = [
        Candidate(candidate_id="candidate-low"),
        Candidate(candidate_id="candidate-high"),
    ]

    match_repository = MagicMock()

    rules_scorer = MagicMock()
    rules_scorer.score.side_effect = [40.0, 90.0]

    evidence_scorer = MagicMock()
    evidence_scorer.score.side_effect = [40.0, 90.0]

    pipeline = MatchingPipeline(
        retriever=retriever,
        candidate_repository=candidate_repository,
        match_repository=match_repository,
        rules_scorer=rules_scorer,
        evidence_scorer=evidence_scorer,
    )

    job = JobDescription(
        job_id="job-1",
        title="Data Engineer",
    )

    results = pipeline.match(job)

    assert results[0].candidate_id == "candidate-high"
    assert results[0].rank == 1
    assert results[1].candidate_id == "candidate-low"
    assert results[1].rank == 2
