"""Tests for the Candidate domain model."""

from candidate_intelligence.domain.candidate import (
    Candidate,
    EducationEntry,
    WorkExperienceEntry,
)


def test_candidate_can_be_created_with_minimal_fields() -> None:
    """Verify a Candidate can be created with only candidate_id."""
    candidate = Candidate(candidate_id="candidate-1")

    assert candidate.candidate_id == "candidate-1"
    assert candidate.full_name is None
    assert candidate.skills == []
    assert candidate.education == []
    assert candidate.work_experience == []


def test_candidate_can_be_created_with_full_fields() -> None:
    """Verify a Candidate can be created with all fields populated."""
    candidate = Candidate(
        candidate_id="candidate-1",
        full_name="Nikhil Chamle",
        email="nikhil@example.com",
        phone="1234567890",
        total_experience_years=5.5,
        skills=["Python", "FastAPI"],
        education=[
            EducationEntry(degree="B.Tech", institution="XYZ University", year="2018")
        ],
        work_experience=[
            WorkExperienceEntry(
                title="Software Engineer",
                company="Acme Corp",
                duration="2018-2023",
                description="Built backend systems.",
            )
        ],
        summary="Experienced backend engineer.",
    )

    assert candidate.full_name == "Nikhil Chamle"
    assert candidate.skills == ["Python", "FastAPI"]
    assert candidate.education[0].degree == "B.Tech"
    assert candidate.work_experience[0].title == "Software Engineer"
