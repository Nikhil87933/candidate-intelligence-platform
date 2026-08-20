"""MinIO object storage client."""

from minio import Minio

from candidate_intelligence.config.settings import Settings


def build_minio_client(settings: Settings) -> Minio:
    """Create a configured MinIO client from application settings."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
