"""
FastAPI application factory.

    uvicorn review_sentiment.api.app:create_app --factory --reload
    Swagger UI: http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from review_sentiment import __version__
from review_sentiment.api.container import ClassifierFactory, Container, build_review_classifier
from review_sentiment.api.errors import register_error_handlers
from review_sentiment.api.middleware import register_middleware
from review_sentiment.api.routers import classifications, health, model
from review_sentiment.core.config import Settings, get_settings
from review_sentiment.core.logging import configure_logging
from review_sentiment.domain.errors import ModelNotAvailableError

logger = logging.getLogger(__name__)

API_V1_ROUTERS = (classifications.router, model.router)


def create_app(
    settings: Settings | None = None,
    classifier_factory: ClassifierFactory = build_review_classifier,
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load the model once at startup (not on the first request). If it is missing the
        # API still starts: /health/ready reports 503 and explains why.
        container: Container = app.state.container
        try:
            container.classifier = await run_in_threadpool(classifier_factory, settings)
            logger.info("Model %s loaded", container.classifier.model_card.version)
        except (ModelNotAvailableError, FileNotFoundError) as exc:
            container.startup_error = str(exc)
            logger.error("Model not loaded: %s", exc)
        yield

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Classifies product reviews as positive, neutral or negative "
                    "(sentence embeddings + classical ML).",
        lifespan=lifespan,
    )
    app.state.container = Container(settings=settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Server-Timing"],
    )
    register_middleware(app)
    register_error_handlers(app)

    api_v1 = APIRouter(prefix="/api/v1")
    for router in API_V1_ROUTERS:
        api_v1.include_router(router)
    app.include_router(health.router)
    app.include_router(api_v1)

    # Production: serve the built front end on "/" (mounted last, so API routes win)
    if settings.static_dir and settings.static_dir.is_dir():
        app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="web")
        logger.info("Serving front end from %s", settings.static_dir)
    return app
