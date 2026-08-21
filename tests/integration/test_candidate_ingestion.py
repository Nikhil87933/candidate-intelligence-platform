"""Integration test for the candidate ingestion workflow."""

from __future__ import annotations

import json

from candidate_intelligence.ingestion.candidate.narrative_builder import (
    build_candidate_narrative,
)
from candidate_intelligence.ingestion.candidate.profile_builder import (
    build_candidate_profile,
)
from candidate_intelligence.ingestion.candidate.upload_handler import (
    handle_resume_upload,
)
from candidate_intelligence.persistence.object_store.repository import StoredObject


class FakeResumeObjectRepository:
    """In-memory object store used for integration testing."""

    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}

    def upload(
        self,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> StoredObject:
        self.uploaded[object_key] = data
        return StoredObject(bucket="resumes", object_key=object_key)


class FakeLLMClient:
    """Deterministic LLM substitute for integration testing."""

    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate_json(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


def test_candidate_ingestion_flow() -> None:
    """Verify upload, profile building, and narrative creation work together."""
    repository = FakeResumeObjectRepository()

    upload = handle_resume_upload(
        repository=repository,
        filename="nikhil_resume.pdf",
        content_type="application/pdf",
        data=b"fake-resume-pdf-content",
        candidate_id="candidate-001",
    )

    llm_response = json.dumps(
        {
            "full_name": "Nikhil Chamle",
            "email": "nikhil@example.com",
            "phone": "+91-9999999999",
            "total_experience_years": 5.0,
            "skills": ["Python", "FastAPI", "SQL"],
            "education": [],
            "work_experience": [],
            "summary": "Backend and data engineering candidate.",
        }
    )

    llm_client = FakeLLMClient(llm_response)

    candidate = build_candidate_profile(
        llm_client=llm_client,
        candidate_id=upload.candidate_id,
        resume_text="Nikhil has experience in Python, FastAPI, and SQL.",
    )

    narrative = build_candidate_narrative(candidate)

    assert upload.candidate_id == "candidate-001"
    assert upload.stored_object.object_key == "candidate-001/nikhil_resume.pdf"
    assert (
        repository.uploaded["candidate-001/nikhil_resume.pdf"]
        == b"fake-resume-pdf-content"
    )

    assert candidate.candidate_id == "candidate-001"
    assert candidate.full_name == "Nikhil Chamle"
    assert candidate.skills == ["Python", "FastAPI", "SQL"]

    assert len(llm_client.prompts) == 1
    assert "Python, FastAPI, and SQL" in llm_client.prompts[0]

    assert "Candidate: Nikhil Chamle." in narrative
    assert "Skills: Python, FastAPI, SQL." in narrative
    assert "Summary: Backend and data engineering candidate." in narrative
