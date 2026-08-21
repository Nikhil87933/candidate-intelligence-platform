"""Pydantic schemas for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from candidate_intelligence.domain.candidate import Candidate
from candidate_intelligence.domain.job_description import JobDescription
from candidate_intelligence.domain.match_result import MatchResult


class CandidateResponse(BaseModel):
    """Response returned after candidate ingestion."""

    candidate: Candidate


class JobCreateRequest(BaseModel):
    """Request body for job description ingestion."""

    jd_text: str = Field(min_length=1)


class JobResponse(BaseModel):
    """Response returned after job ingestion."""

    job: JobDescription


class MatchRunRequest(BaseModel):
    """Options for running candidate matching."""

    limit: int = Field(default=10, ge=1, le=100)


class MatchResultsResponse(BaseModel):
    """Response containing ranked candidate matches."""

    matches: list[MatchResult] = Field(default_factory=list)
