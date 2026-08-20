"""Job description domain model."""

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    """Structured job requirements extracted from a job description."""

    job_id: str
    title: str | None = None
    company: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    min_experience_years: float | None = None
    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    summary: str | None = None
