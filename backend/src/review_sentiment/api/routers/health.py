"""Liveness (is the process up?) and readiness (can it serve predictions?) probes."""

from fastapi import APIRouter, Response, status

from review_sentiment import __version__
from review_sentiment.api.dependencies import ContainerDep
from review_sentiment.api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get("/ready", response_model=HealthResponse,
            responses={503: {"model": HealthResponse, "description": "Model not loaded"}})
async def ready(container: ContainerDep, response: Response) -> HealthResponse:
    if not container.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="unavailable", version=__version__,
                              detail=container.startup_error)
    return HealthResponse(status="ok", version=__version__,
                          model_version=container.classifier.model_card.version)
