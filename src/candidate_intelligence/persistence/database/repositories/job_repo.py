"""Repository for job description persistence."""

from __future__ import annotations

from sqlalchemy.orm import Session

from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.persistence.database.models import JobModel


class JobRepository:
    """Handles persistence of JobDescription records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, job: JobDescription, jd_text: str | None = None) -> None:
        """Insert or update a job record."""
        model = self._session.get(JobModel, job.job_id)
        if model is None:
            model = JobModel(job_id=job.job_id)
            self._session.add(model)

        model.title = job.title
        model.company = job.company
        model.required_skills = job.required_skills
        model.min_experience_years = job.min_experience_years
        model.responsibilities = job.responsibilities
        model.qualifications = job.qualifications
        model.summary = job.summary
        model.jd_text = jd_text

    def get(self, job_id: str) -> JobDescription | None:
        """Retrieve a job by id, or None if not found."""
        model = self._session.get(JobModel, job_id)
        if model is None:
            return None

        return JobDescription(
            job_id=model.job_id,
            title=model.title,
            company=model.company,
            required_skills=model.required_skills,
            min_experience_years=model.min_experience_years,
            responsibilities=model.responsibilities,
            qualifications=model.qualifications,
            summary=model.summary,
        )
