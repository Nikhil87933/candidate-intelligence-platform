"""Tests for job description intake handling."""

import pytest

from candidate_intelligence.ingestion.job.intake_handler import (
    EmptyJobDescriptionError,
    handle_job_intake,
)


def test_handle_job_intake_generates_job_id() -> None:
    """Verify job intake generates a job id when none is provided."""
    result = handle_job_intake("We are hiring a backend engineer.")

    assert result.job_id
    assert result.jd_text == "We are hiring a backend engineer."


def test_handle_job_intake_uses_provided_job_id() -> None:
    """Verify job intake respects an explicit job id."""
    result = handle_job_intake("JD text here", job_id="job-123")

    assert result.job_id == "job-123"


def test_handle_job_intake_strips_whitespace() -> None:
    """Verify job intake strips leading/trailing whitespace."""
    result = handle_job_intake("   JD text here   ")

    assert result.jd_text == "JD text here"


def test_handle_job_intake_rejects_empty_text() -> None:
    """Verify job intake rejects empty or whitespace-only text."""
    with pytest.raises(EmptyJobDescriptionError, match="must not be empty"):
        handle_job_intake("   ")
