"""
FastAPI application factory.

Initializes the FastAPI app with middleware, routers,
lifecycle events, and health checks.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_v1_router
from src.core.config import get_settings
from src.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle — startup and shutdown events."""
    # ── Startup ──────────────────────────────────────────────────
    setup_logging()
    settings = get_settings()
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Attempt to load ML models (non-blocking)
    try:
        from src.services.disease_service import load_disease_model
        await load_disease_model()
    except Exception as e:
        logger.warning("disease_model_load_failed", error=str(e))





    logger.info("application_started")

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-powered healthcare platform providing disease prediction, "
            "drug recommendations, and a RAG-based medical chatbot."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(api_v1_router)

    # ── Health Check ─────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Application health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    return app


# Application instance for uvicorn
app = create_app()
