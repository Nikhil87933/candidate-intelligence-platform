"""Candidate API routes."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, UploadFile, status

from candidate_intelligence.api.schemas import CandidateResponse
from candidate_intelligence.config.settings import Settings
from candidate_intelligence.embeddings.embedder import OllamaEmbedder
from candidate_intelligence.extraction.docx_extractor import extract_docx_text
from candidate_intelligence.extraction.ocr_extractor import extract_ocr_text
from candidate_intelligence.extraction.pdf_extractor import extract_pdf_text
from candidate_intelligence.ingestion.candidate.narrative_builder import (
    build_candidate_narrative,
)
from candidate_intelligence.ingestion.candidate.profile_builder import (
    build_candidate_profile,
)
from candidate_intelligence.ingestion.candidate.upload_handler import (
    UnsupportedResumeFileType,
    handle_resume_upload,
)
from candidate_intelligence.llm.client import OllamaClient
from candidate_intelligence.persistence.database.db import (
    build_engine,
    build_session_factory,
    session_scope,
)
from candidate_intelligence.persistence.database.repositories.candidate_repo import (
    CandidateRepository,
)
from candidate_intelligence.persistence.object_store.client import build_minio_client
from candidate_intelligence.persistence.object_store.repository import (
    ResumeObjectRepository,
)
from candidate_intelligence.vector.client import build_qdrant_client
from candidate_intelligence.vector.index import CandidateVectorIndex

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post(
    "/upload",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_candidate(file: UploadFile) -> CandidateResponse:
    """Upload, understand, persist, and index a candidate resume."""
    settings = Settings()

    filename = file.filename
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    minio_client = build_minio_client(settings)
    object_repository = ResumeObjectRepository(
        client=minio_client,
        bucket=settings.minio_bucket_resumes,
    )

    try:
        upload = handle_resume_upload(
            repository=object_repository,
            filename=filename,
            content_type=content_type,
            data=content,
        )
    except UnsupportedResumeFileType as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    suffix = Path(filename).suffix.lower()

    with NamedTemporaryFile(suffix=suffix, delete=True) as temporary_file:
        temporary_file.write(content)
        temporary_file.flush()
        temporary_path = Path(temporary_file.name)

        if suffix == ".pdf":
            extracted_text = extract_pdf_text(temporary_path)
            if not extracted_text.strip():
                extracted_text = extract_ocr_text(temporary_path)
        elif suffix == ".docx":
            extracted_text = extract_docx_text(temporary_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported resume file type.",
            )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text could be extracted from the resume.",
        )

    llm_client = OllamaClient(settings)

    candidate = build_candidate_profile(
        llm_client=llm_client,
        candidate_id=upload.candidate_id,
        resume_text=extracted_text,
    )

    narrative = build_candidate_narrative(candidate)

    engine = build_engine(settings)
    session_factory = build_session_factory(engine)

    with session_scope(session_factory) as session:
        candidate_repository = CandidateRepository(session)

        candidate_repository.save(
            candidate=candidate,
            narrative=narrative,
            resume_object_key=upload.stored_object.object_key,
        )

    embedder = OllamaEmbedder(settings)
    qdrant_client = build_qdrant_client(settings)

    vector_index = CandidateVectorIndex(
        client=qdrant_client,
        collection_name=settings.qdrant_collection_candidates,
        vector_size=settings.embedding_vector_size,
    )

    vector_index.upsert(
        candidate_id=candidate.candidate_id,
        vector=embedder.embed(narrative),
    )

    return CandidateResponse(candidate=candidate)
