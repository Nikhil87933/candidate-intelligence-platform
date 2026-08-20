"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Candidate Intelligence Platform"
    app_env: str = "development"
    debug: bool = False

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    minio_bucket_resumes: str = "resumes"

    qdrant_host: str
    qdrant_port: int = 6333

    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "qwen2.5:3b"

    @property
    def database_url(self) -> str:
        """Build the PostgreSQL SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def qdrant_url(self) -> str:
        """Build the Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def ollama_url(self) -> str:
        """Build the Ollama connection URL."""
        return f"http://{self.ollama_host}:{self.ollama_port}"
