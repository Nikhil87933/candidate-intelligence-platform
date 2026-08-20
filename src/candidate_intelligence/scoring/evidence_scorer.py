"""Evidence-based candidate scoring from resume content."""

from __future__ import annotations

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription


class EvidenceScorer:
    """Score how strongly a candidate profile provides evidence for requirements."""

    def score(
        self,
        candidate: Candidate,
        job: JobDescription,
    ) -> float:
        """Calculate an evidence score from 0 to 100."""
        required_skills = [
            skill.strip().lower() for skill in job.required_skills if skill.strip()
        ]

        if not required_skills:
            return 0.0

        evidence_text = self._build_evidence_text(candidate)

        matched_skills = sum(1 for skill in required_skills if skill in evidence_text)

        return (matched_skills / len(required_skills)) * 100

    @staticmethod
    def _build_evidence_text(candidate: Candidate) -> str:
        """Combine candidate profile fields that provide textual evidence."""
        parts = [
            candidate.summary or "",
            *candidate.skills,
        ]

        for experience in candidate.work_experience:
            parts.extend(
                [
                    experience.title,
                    experience.description or "",
                ]
            )

        return "\n".join(parts).lower()
