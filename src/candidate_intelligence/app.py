"""FastAPI application factory."""

from fastapi import FastAPI

from candidate_intelligence.api.routes_candidates import router as candidates_router
from candidate_intelligence.api.routes_jobs import router as jobs_router
from candidate_intelligence.api.routes_matching import router as matching_router
from candidate_intelligence.config.settings import Settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.include_router(candidates_router)
    app.include_router(jobs_router)
    app.include_router(matching_router)

    return app


app = create_app()
