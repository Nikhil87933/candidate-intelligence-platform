"""Tests for candidate resume upload handling."""

import pytest

from candidate_intelligence.ingestion.candidate.upload_handler import (
    UnsupportedResumeFileType,
    handle_resume_upload,
)
from candidate_intelligence.persistence.object_store.repository import StoredObject


class FakeResumeObjectRepository:
    """In-memory stand-in for ResumeObjectRepository used in tests."""

    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}

    def upload(self, object_key: str, data: bytes, content_type: str) -> StoredObject:
        self.uploaded[object_key] = data
        return StoredObject(bucket="resumes", object_key=object_key)


def test_handle_resume_upload_pdf_generates_candidate_id() -> None:
    """Verify a PDF upload is stored and assigned a candidate id."""
    repository = FakeResumeObjectRepository()

    result = handle_resume_upload(
        repository,
        filename="resume.pdf",
        content_type="application/pdf",
        data=b"pdf-bytes",
    )

    assert result.candidate_id
    assert result.original_filename == "resume.pdf"
    assert result.stored_object.object_key == f"{result.candidate_id}/resume.pdf"
    assert repository.uploaded[result.stored_object.object_key] == b"pdf-bytes"


def test_handle_resume_upload_uses_provided_candidate_id() -> None:
    """Verify an explicit candidate id is respected instead of generating one."""
    repository = FakeResumeObjectRepository()

    result = handle_resume_upload(
        repository,
        filename="resume.docx",
        content_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        data=b"docx-bytes",
        candidate_id="candidate-123",
    )

    assert result.candidate_id == "candidate-123"
    assert result.stored_object.object_key == "candidate-123/resume.docx"


def test_handle_resume_upload_rejects_unsupported_content_type() -> None:
    """Verify unsupported file types raise a clear error."""
    repository = FakeResumeObjectRepository()

    with pytest.raises(UnsupportedResumeFileType, match="Unsupported resume"):
        handle_resume_upload(
            repository,
            filename="resume.txt",
            content_type="text/plain",
            data=b"plain-bytes",
        )
