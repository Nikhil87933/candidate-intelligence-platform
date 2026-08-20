"""Tests for database engine and session utilities."""

from sqlalchemy import text

from candidate_intelligence.config.settings import Settings
from candidate_intelligence.persistence.database.db import (
    build_engine,
    build_session_factory,
    session_scope,
)


def _build_sqlite_settings() -> Settings:
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
    return settings


def test_build_engine_creates_engine() -> None:
    """Verify build_engine returns a usable SQLAlchemy engine."""
    settings = _build_sqlite_settings()

    engine = build_engine(settings)

    assert str(engine.url).startswith("postgresql+psycopg2://")


def test_session_scope_commits_on_success() -> None:
    """Verify session_scope commits changes when no exception occurs."""
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///:memory:")
    engine.connect().execute(text("CREATE TABLE t (id INTEGER)")).connection.commit()
    session_factory = build_session_factory(engine)

    with session_scope(session_factory) as session:
        session.execute(text("INSERT INTO t (id) VALUES (1)"))

    with session_factory() as session:
        result = session.execute(text("SELECT COUNT(*) FROM t")).scalar()

    assert result == 1


def test_session_scope_rolls_back_on_error() -> None:
    """Verify session_scope rolls back changes when an exception occurs."""
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///:memory:")
    engine.connect().execute(text("CREATE TABLE t (id INTEGER)")).connection.commit()
    session_factory = build_session_factory(engine)

    try:
        with session_scope(session_factory) as session:
            session.execute(text("INSERT INTO t (id) VALUES (1)"))
            raise ValueError("boom")
    except ValueError:
        pass

    with session_factory() as session:
        result = session.execute(text("SELECT COUNT(*) FROM t")).scalar()

    assert result == 0
