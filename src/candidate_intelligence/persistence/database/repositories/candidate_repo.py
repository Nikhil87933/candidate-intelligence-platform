"""Repository for candidate persistence."""

from __future__ import annotations

from sqlalchemy.orm import Session

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.persistence.database.models import CandidateModel


class CandidateRepository:
    """Handles persistence of Candidate profiles."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        candidate: Candidate,
        narrative: str | None = None,
        resume_object_key: str | None = None,
    ) -> None:
        """Insert or update a candidate record."""
        model = self._session.get(CandidateModel, candidate.candidate_id)
        if model is None:
            model = CandidateModel(candidate_id=candidate.candidate_id)
            self._session.add(model)

        model.full_name = candidate.full_name
        model.email = candidate.email
        model.phone = candidate.phone
        model.total_experience_years = candidate.total_experience_years
        model.skills = candidate.skills
        model.education = [entry.model_dump() for entry in candidate.education]
        model.work_experience = [
            entry.model_dump() for entry in candidate.work_experience
        ]
        model.summary = candidate.summary
        model.narrative = narrative
        model.resume_object_key = resume_object_key

    def get(self, candidate_id: str) -> Candidate | None:
        """Retrieve a candidate by id, or None if not found."""
        model = self._session.get(CandidateModel, candidate_id)
        if model is None:
            return None

        return Candidate.model_validate(
            {
                "candidate_id": model.candidate_id,
                "full_name": model.full_name,
                "email": model.email,
                "phone": model.phone,
                "total_experience_years": model.total_experience_years,
                "skills": model.skills,
                "education": model.education,
                "work_experience": model.work_experience,
                "summary": model.summary,
            }
        )
