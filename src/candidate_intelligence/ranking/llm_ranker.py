"""LLM-based final ranking for shortlisted candidate matches."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult
from candidate_intelligence.llm.client import OllamaClient


class CandidateRanking(BaseModel):
    """Final ranking assigned by the LLM to a candidate."""

    candidate_id: str
    rank: int = Field(ge=1)
    final_score: float = Field(ge=0, le=100)
    rationale: str


class RankingResponse(BaseModel):
    """Structured response returned by the LLM ranking step."""

    rankings: list[CandidateRanking] = Field(default_factory=list)


class LLMFinalRanker:
    """Use an LLM to comparatively rank shortlisted candidates."""

    def __init__(self, llm_client: OllamaClient) -> None:
        self._llm_client = llm_client

    def rank(
        self,
        job: JobDescription,
        candidates: list[Candidate],
        matches: list[MatchResult],
    ) -> list[MatchResult]:
        """Rank shortlisted candidates and attach final scores and rationales."""
        if not matches:
            return []

        prompt = self._build_prompt(
            job=job,
            candidates=candidates,
            matches=matches,
        )

        response_text = self._llm_client.generate_json(prompt)
        response = RankingResponse.model_validate_json(response_text)

        rankings_by_candidate = {
            ranking.candidate_id: ranking for ranking in response.rankings
        }

        ranked_matches: list[MatchResult] = []

        for match in matches:
            ranking = rankings_by_candidate.get(match.candidate_id)

            if ranking is None:
                ranked_matches.append(match)
                continue

            ranked_matches.append(
                match.model_copy(
                    update={
                        "rank": ranking.rank,
                        "final_score": ranking.final_score,
                        "rationale": ranking.rationale,
                    }
                )
            )

        return sorted(
            ranked_matches,
            key=lambda match: match.rank or float("inf"),
        )

    @staticmethod
    def _build_prompt(
        job: JobDescription,
        candidates: list[Candidate],
        matches: list[MatchResult],
    ) -> str:
        """Build the comparative ranking prompt."""
        candidates_by_id = {
            candidate.candidate_id: candidate for candidate in candidates
        }

        shortlisted_candidates = []

        for match in matches:
            candidate = candidates_by_id.get(match.candidate_id)

            if candidate is None:
                continue

            shortlisted_candidates.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "full_name": candidate.full_name,
                    "total_experience_years": (candidate.total_experience_years),
                    "skills": candidate.skills,
                    "summary": candidate.summary,
                    "rules_score": match.rules_score,
                    "evidence_score": match.evidence_score,
                    "deterministic_score": match.final_score,
                }
            )

        job_data = {
            "job_id": job.job_id,
            "title": job.title,
            "required_skills": job.required_skills,
            "min_experience_years": job.min_experience_years,
            "responsibilities": job.responsibilities,
            "qualifications": job.qualifications,
            "summary": job.summary,
        }

        return (
            "You are a candidate ranking system. "
            "Compare the shortlisted candidates against the job requirements. "
            "Use the deterministic scores as evidence, but independently assess "
            "overall candidate suitability. Rank every provided candidate exactly "
            "once. Return valid JSON only with this structure: "
            '{"rankings":[{"candidate_id":"...","rank":1,'
            '"final_score":0-100,"rationale":"..."}]}. '
            "Do not add candidates that were not provided. "
            "Do not omit any provided candidate.\n\n"
            f"JOB:\n{json.dumps(job_data)}\n\n"
            f"CANDIDATES:\n{json.dumps(shortlisted_candidates)}"
        )
