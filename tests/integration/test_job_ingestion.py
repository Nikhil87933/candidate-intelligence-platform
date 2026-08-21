"""Integration test for the job ingestion workflow."""

from __future__ import annotations

import json

from candidate_intelligence.ingestion.job.intake_handler import handle_job_intake
from candidate_intelligence.ingestion.job.requirement_builder import (
    build_job_requirements,
)


class FakeLLMClient:
    """Deterministic LLM substitute for integration testing."""

    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate_json(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


def test_job_ingestion_flow() -> None:
    """Verify job intake and requirement building work together."""
    jd_text = """
    We are looking for a Python Backend Engineer.

    Required skills:
    - Python
    - FastAPI
    - SQL

    Minimum experience: 3 years.

    The candidate will build backend APIs and work with databases.
    """

    intake = handle_job_intake(
        jd_text=jd_text,
        job_id="job-001",
    )

    llm_response = json.dumps(
        {
            "title": "Python Backend Engineer",
            "company": "Acme Corp",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "min_experience_years": 3.0,
            "responsibilities": [
                "Build backend APIs",
                "Work with databases",
            ],
            "qualifications": [
                "Experience with backend development",
            ],
            "summary": "Python backend engineering role.",
        }
    )

    llm_client = FakeLLMClient(llm_response)

    job = build_job_requirements(
        llm_client=llm_client,
        job_id=intake.job_id,
        jd_text=intake.jd_text,
    )

    assert intake.job_id == "job-001"
    assert "Python Backend Engineer" in intake.jd_text

    assert job.job_id == "job-001"
    assert job.title == "Python Backend Engineer"
    assert job.required_skills == ["Python", "FastAPI", "SQL"]
    assert job.min_experience_years == 3.0

    assert len(llm_client.prompts) == 1
    assert "Python Backend Engineer" in llm_client.prompts[0]

    assert "Build backend APIs" in job.responsibilities
    assert "Work with databases" in job.responsibilities
