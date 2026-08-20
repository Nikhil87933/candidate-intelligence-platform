"""Repository for storing and retrieving resume files in object storage."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from minio import Minio


@dataclass(frozen=True)
class StoredObject:
    """Reference to an object stored in object storage."""

    bucket: str
    object_key: str


class ResumeObjectRepository:
    """Handles resume file persistence in MinIO object storage."""

    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def upload(self, object_key: str, data: bytes, content_type: str) -> StoredObject:
        """Upload resume bytes to the bucket and return a reference."""
        self._client.put_object(
            self._bucket,
            object_key,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return StoredObject(bucket=self._bucket, object_key=object_key)

    def download(self, object_key: str) -> bytes:
        """Download resume bytes from the bucket."""
        response = self._client.get_object(self._bucket, object_key)
        try:
            return bytes(response.read())
        finally:
            response.close()
            response.release_conn()
