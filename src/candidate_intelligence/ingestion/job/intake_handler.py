"""Handles incoming job description intake."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


class EmptyJobDescriptionError(ValueError):
    """Raised when a submitted job description text is empty."""


@dataclass(frozen=True)
class JobIntake:
    """Result of handling a job description intake."""

    job_id: str
    jd_text: str


def handle_job_intake(jd_text: str, job_id: str | None = None) -> JobIntake:
    """Validate and register an incoming job description submission."""
    stripped_text = jd_text.strip()
    if not stripped_text:
        raise EmptyJobDescriptionError("Job description text must not be empty.")

    resolved_job_id = job_id or str(uuid.uuid4())

    return JobIntake(job_id=resolved_job_id, jd_text=stripped_text)
