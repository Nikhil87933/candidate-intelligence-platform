"""Tests for deterministic candidate scoring."""

from candidate_intelligence.domain.candidate import (
    Candidate,
    WorkExperienceEntry,
)
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.scoring.evidence_scorer import EvidenceScorer
from candidate_intelligence.scoring.rules_scorer import RulesScorer


def test_rules_scorer_returns_full_score_for_perfect_match() -> None:
    """Verify a candidate meeting all requirements receives 100."""
    candidate = Candidate(
        candidate_id="candidate-1",
        skills=["Python", "SQL", "Spark"],
        total_experience_years=5,
    )

    job = JobDescription(
        job_id="job-1",
        required_skills=["Python", "SQL", "Spark"],
        min_experience_years=5,
    )

    score = RulesScorer().score(candidate, job)

    assert score == 100.0


def test_rules_scorer_applies_skill_and_experience_matching() -> None:
    """Verify partial requirement matches produce a partial score."""
    candidate = Candidate(
        candidate_id="candidate-1",
        skills=["Python", "SQL"],
        total_experience_years=2,
    )

    job = JobDescription(
        job_id="job-1",
        required_skills=["Python", "SQL", "Spark", "Airflow"],
        min_experience_years=4,
    )

    score = RulesScorer().score(candidate, job)

    assert score == 50.0


def test_rules_scorer_normalizes_when_only_skills_are_required() -> None:
    """Verify missing experience requirements do not penalize skill scoring."""
    candidate = Candidate(
        candidate_id="candidate-1",
        skills=["Python"],
    )

    job = JobDescription(
        job_id="job-1",
        required_skills=["Python"],
    )

    score = RulesScorer().score(candidate, job)

    assert score == 100.0


def test_evidence_scorer_finds_skills_in_candidate_evidence() -> None:
    """Verify evidence score uses actual candidate profile content."""
    candidate = Candidate(
        candidate_id="candidate-1",
        summary="Experienced backend engineer building Python services.",
        work_experience=[
            WorkExperienceEntry(
                title="Data Engineer",
                company="Example Corp",
                description="Built Spark data pipelines.",
            )
        ],
    )

    job = JobDescription(
        job_id="job-1",
        required_skills=["Python", "Spark", "Airflow"],
    )

    score = EvidenceScorer().score(candidate, job)

    assert score == (2 / 3) * 100


def test_evidence_scorer_returns_zero_without_job_skills() -> None:
    """Verify evidence scoring returns zero when there is nothing to score."""
    candidate = Candidate(
        candidate_id="candidate-1",
        summary="Python developer",
    )

    job = JobDescription(job_id="job-1")

    score = EvidenceScorer().score(candidate, job)

    assert score == 0.0
