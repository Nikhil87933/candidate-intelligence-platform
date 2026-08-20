"""Tests for the JobDescription domain model."""

from candidate_intelligence.domain.job_description import JobDescription


def test_job_description_can_be_created_with_minimal_fields() -> None:
    """Verify a JobDescription can be created with only job_id."""
    job = JobDescription(job_id="job-1")

    assert job.job_id == "job-1"
    assert job.title is None
    assert job.required_skills == []
    assert job.responsibilities == []
    assert job.qualifications == []


def test_job_description_can_be_created_with_full_fields() -> None:
    """Verify a JobDescription can be created with all fields populated."""
    job = JobDescription(
        job_id="job-1",
        title="Backend Engineer",
        company="Acme Corp",
        required_skills=["Python", "FastAPI"],
        min_experience_years=3.0,
        responsibilities=["Build APIs", "Review code"],
        qualifications=["B.Tech in CS"],
        summary="Backend role focused on scalable APIs.",
    )

    assert job.title == "Backend Engineer"
    assert job.required_skills == ["Python", "FastAPI"]
    assert job.min_experience_years == 3.0
