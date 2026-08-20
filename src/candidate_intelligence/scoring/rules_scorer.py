"""Deterministic rule-based candidate scoring."""

from __future__ import annotations

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.scoring.weights import (
    EXPERIENCE_MATCH_WEIGHT,
    SKILL_MATCH_WEIGHT,
)


class RulesScorer:
    """Score candidates using explicit job requirements."""

    def score(
        self,
        candidate: Candidate,
        job: JobDescription,
    ) -> float:
        """Calculate a deterministic rules score from 0 to 100."""
        weighted_scores: list[tuple[float, float]] = []

        if job.required_skills:
            weighted_scores.append(
                (
                    SKILL_MATCH_WEIGHT,
                    self._score_skills(candidate, job),
                )
            )

        if job.min_experience_years is not None:
            weighted_scores.append(
                (
                    EXPERIENCE_MATCH_WEIGHT,
                    self._score_experience(candidate, job),
                )
            )

        if not weighted_scores:
            return 0.0

        total_weight = sum(weight for weight, _ in weighted_scores)
        weighted_total = sum(weight * score for weight, score in weighted_scores)

        return weighted_total / total_weight

    @staticmethod
    def _score_skills(
        candidate: Candidate,
        job: JobDescription,
    ) -> float:
        """Calculate the percentage of required skills matched."""
        required_skills = {
            skill.strip().lower() for skill in job.required_skills if skill.strip()
        }

        if not required_skills:
            return 0.0

        candidate_skills = {
            skill.strip().lower() for skill in candidate.skills if skill.strip()
        }

        matched_skills = required_skills.intersection(candidate_skills)

        return (len(matched_skills) / len(required_skills)) * 100

    @staticmethod
    def _score_experience(
        candidate: Candidate,
        job: JobDescription,
    ) -> float:
        """Calculate how well candidate experience meets the requirement."""
        required_experience = job.min_experience_years

        if required_experience is None or required_experience <= 0:
            return 0.0

        candidate_experience = candidate.total_experience_years or 0.0

        return min(candidate_experience / required_experience, 1.0) * 100
