"""Tests for database repositories using an in-memory SQLite database."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from candidate_intelligence.domain.candidate import Candidate, WorkExperienceEntry
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.persistence.database.models import Base
from candidate_intelligence.persistence.database.repositories.candidate_repo import (
    CandidateRepository,
)
from candidate_intelligence.persistence.database.repositories.job_repo import (
    JobRepository,
)
from candidate_intelligence.persistence.database.repositories.match_repo import (
    MatchRepository,
)


@pytest.fixture
def session() -> Iterator[Session]:
    """Provide a fresh in-memory SQLite session with all tables created."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def test_candidate_repository_save_and_get(session: Session) -> None:
    """Verify a candidate can be saved and retrieved."""
    repo = CandidateRepository(session)
    candidate = Candidate(
        candidate_id="candidate-1",
        full_name="Nikhil Chamle",
        skills=["Python"],
        work_experience=[WorkExperienceEntry(title="Engineer", company="Acme Corp")],
    )

    repo.save(candidate, narrative="Candidate narrative text.")
    session.commit()

    result = repo.get("candidate-1")

    assert result is not None
    assert result.full_name == "Nikhil Chamle"
    assert result.skills == ["Python"]
    assert result.work_experience[0].title == "Engineer"


def test_candidate_repository_get_missing_returns_none(session: Session) -> None:
    """Verify getting a missing candidate returns None."""
    repo = CandidateRepository(session)

    assert repo.get("does-not-exist") is None


def test_candidate_repository_save_updates_existing(session: Session) -> None:
    """Verify saving an existing candidate id updates the record."""
    repo = CandidateRepository(session)
    repo.save(Candidate(candidate_id="candidate-1", full_name="Old Name"))
    session.commit()

    repo.save(Candidate(candidate_id="candidate-1", full_name="New Name"))
    session.commit()

    result = repo.get("candidate-1")

    assert result is not None
    assert result.full_name == "New Name"


def test_job_repository_save_and_get(session: Session) -> None:
    """Verify a job can be saved and retrieved."""
    repo = JobRepository(session)
    job = JobDescription(
        job_id="job-1", title="Backend Engineer", required_skills=["Python"]
    )

    repo.save(job, jd_text="We are hiring.")
    session.commit()

    result = repo.get("job-1")

    assert result is not None
    assert result.title == "Backend Engineer"
    assert result.required_skills == ["Python"]


def test_job_repository_get_missing_returns_none(session: Session) -> None:
    """Verify getting a missing job returns None."""
    repo = JobRepository(session)

    assert repo.get("does-not-exist") is None


def test_match_repository_save_and_get_for_job(session: Session) -> None:
    """Verify match results can be saved and retrieved ordered by rank."""
    JobRepository(session).save(JobDescription(job_id="job-1"))
    CandidateRepository(session).save(Candidate(candidate_id="candidate-1"))
    CandidateRepository(session).save(Candidate(candidate_id="candidate-2"))
    session.commit()

    match_repo = MatchRepository(session)
    match_repo.save(
        MatchResult(job_id="job-1", candidate_id="candidate-2", final_score=0.7, rank=2)
    )
    match_repo.save(
        MatchResult(job_id="job-1", candidate_id="candidate-1", final_score=0.9, rank=1)
    )
    session.commit()

    results = match_repo.get_for_job("job-1")

    assert len(results) == 2
    assert results[0].candidate_id == "candidate-1"
    assert results[0].rank == 1
    assert results[1].candidate_id == "candidate-2"
