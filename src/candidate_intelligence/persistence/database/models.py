"""SQLAlchemy ORM models for candidates, jobs, and matches."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class CandidateModel(Base):
    """Database model for a candidate profile."""

    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    total_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    education: Mapped[list[dict[str, str | None]]] = mapped_column(JSON, default=list)
    work_experience: Mapped[list[dict[str, str | None]]] = mapped_column(
        JSON, default=list
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_object_key: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class JobModel(Base):
    """Database model for a job description."""

    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    min_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    qualifications: Mapped[list[str]] = mapped_column(JSON, default=list)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    jd_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MatchModel(Base):
    """Database model for a candidate-job match result."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String, ForeignKey("jobs.job_id"))
    candidate_id: Mapped[str] = mapped_column(
        String, ForeignKey("candidates.candidate_id")
    )
    rules_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
