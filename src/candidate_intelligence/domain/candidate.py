"""Candidate domain model."""

from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    """A single education record extracted from a resume."""

    degree: str
    institution: str
    year: str | None = None


class WorkExperienceEntry(BaseModel):
    """A single work experience record extracted from a resume."""

    title: str
    company: str
    duration: str | None = None
    description: str | None = None


class Candidate(BaseModel):
    """Structured candidate profile extracted from a resume."""

    candidate_id: str
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    work_experience: list[WorkExperienceEntry] = Field(default_factory=list)
    summary: str | None = None
