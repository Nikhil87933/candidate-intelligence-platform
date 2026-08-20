"""Handles incoming candidate resume uploads."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from candidate_intelligence.persistence.object_store.repository import (
    ResumeObjectRepository,
    StoredObject,
)

SUPPORTED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


class UnsupportedResumeFileType(ValueError):
    """Raised when an uploaded resume file type is not supported."""


@dataclass(frozen=True)
class ResumeUpload:
    """Result of handling a candidate resume upload."""

    candidate_id: str
    stored_object: StoredObject
    original_filename: str


def handle_resume_upload(
    repository: ResumeObjectRepository,
    filename: str,
    content_type: str,
    data: bytes,
    candidate_id: str | None = None,
) -> ResumeUpload:
    """Store an uploaded resume file and return upload metadata."""
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise UnsupportedResumeFileType(
            f"Unsupported resume content type: {content_type}"
        )

    resolved_candidate_id = candidate_id or str(uuid.uuid4())
    object_key = f"{resolved_candidate_id}/{filename}"

    stored_object = repository.upload(
        object_key=object_key, data=data, content_type=content_type
    )

    return ResumeUpload(
        candidate_id=resolved_candidate_id,
        stored_object=stored_object,
        original_filename=filename,
    )
