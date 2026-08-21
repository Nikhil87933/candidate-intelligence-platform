"""Job API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from candidate_intelligence.api.schemas import JobCreateRequest, JobResponse
from candidate_intelligence.config.settings import Settings
from candidate_intelligence.ingestion.job.intake_handler import (
    EmptyJobDescriptionError,
    handle_job_intake,
)
from candidate_intelligence.ingestion.job.requirement_builder import (
    build_job_requirements,
)
from candidate_intelligence.llm.client import OllamaClient
from candidate_intelligence.persistence.database.db import (
    build_engine,
    build_session_factory,
    session_scope,
)
from candidate_intelligence.persistence.database.repositories.job_repo import (
    JobRepository,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(request: JobCreateRequest) -> JobResponse:
    """Understand and persist a job description."""
    settings = Settings()

    try:
        intake = handle_job_intake(request.jd_text)
    except EmptyJobDescriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    llm_client = OllamaClient(settings)

    job = build_job_requirements(
        llm_client=llm_client,
        job_id=intake.job_id,
        jd_text=intake.jd_text,
    )

    engine = build_engine(settings)
    session_factory = build_session_factory(engine)

    with session_scope(session_factory) as session:
        job_repository = JobRepository(session)
        job_repository.save(
            job=job,
            jd_text=intake.jd_text,
        )

    return JobResponse(job=job)
