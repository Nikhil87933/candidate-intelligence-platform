"""Tests for the job requirement builder."""

import json
from unittest.mock import MagicMock

from candidate_intelligence.ingestion.job.requirement_builder import (
    build_job_requirements,
)


def test_build_job_requirements_returns_parsed_job() -> None:
    """Verify the requirement builder calls the LLM and parses the result."""
    llm_client = MagicMock()
    llm_client.generate_json.return_value = json.dumps(
        {
            "title": "Backend Engineer",
            "required_skills": ["Python"],
        }
    )

    job = build_job_requirements(
        llm_client, job_id="job-1", jd_text="job description text here"
    )

    assert job.job_id == "job-1"
    assert job.title == "Backend Engineer"
    assert job.required_skills == ["Python"]
    llm_client.generate_json.assert_called_once()
