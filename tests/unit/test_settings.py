"""Tests for application configuration."""

from candidate_intelligence.config.settings import Settings


def test_settings_can_be_created() -> None:
    """Verify application settings can be instantiated."""
    settings = Settings(
        postgres_host="localhost",
        postgres_db="candidate_intelligence",
        postgres_user="candidate_user",
        postgres_password="candidate_password",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadmin123",
        qdrant_host="localhost",
    )

    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.qdrant_port == 6333
    assert settings.minio_bucket_resumes == "resumes"
