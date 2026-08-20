"""Tests for the resume object store repository."""

from unittest.mock import MagicMock

from candidate_intelligence.persistence.object_store.repository import (
    ResumeObjectRepository,
    StoredObject,
)


def test_repository_creates_bucket_if_missing() -> None:
    """Verify the bucket is created when it does not already exist."""
    client = MagicMock()
    client.bucket_exists.return_value = False

    ResumeObjectRepository(client, bucket="resumes")

    client.bucket_exists.assert_called_once_with("resumes")
    client.make_bucket.assert_called_once_with("resumes")


def test_repository_skips_bucket_creation_if_exists() -> None:
    """Verify the bucket is not recreated when it already exists."""
    client = MagicMock()
    client.bucket_exists.return_value = True

    ResumeObjectRepository(client, bucket="resumes")

    client.make_bucket.assert_not_called()


def test_repository_upload_returns_stored_object() -> None:
    """Verify upload stores bytes and returns a StoredObject reference."""
    client = MagicMock()
    client.bucket_exists.return_value = True
    repository = ResumeObjectRepository(client, bucket="resumes")

    result = repository.upload(
        object_key="candidate-1/resume.pdf",
        data=b"pdf-bytes",
        content_type="application/pdf",
    )

    assert result == StoredObject(bucket="resumes", object_key="candidate-1/resume.pdf")
    client.put_object.assert_called_once()
    call_kwargs = client.put_object.call_args.kwargs
    assert call_kwargs["length"] == len(b"pdf-bytes")
    assert call_kwargs["content_type"] == "application/pdf"


def test_repository_download_reads_and_closes_response() -> None:
    """Verify download returns bytes and releases the connection."""
    client = MagicMock()
    client.bucket_exists.return_value = True
    response = MagicMock()
    response.read.return_value = b"pdf-bytes"
    client.get_object.return_value = response
    repository = ResumeObjectRepository(client, bucket="resumes")

    result = repository.download("candidate-1/resume.pdf")

    assert result == b"pdf-bytes"
    response.close.assert_called_once()
    response.release_conn.assert_called_once()
