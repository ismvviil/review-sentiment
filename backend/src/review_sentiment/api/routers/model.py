from fastapi import APIRouter

from review_sentiment.api.dependencies import ClassifierDep
from review_sentiment.api.schemas import ModelCardResponse

router = APIRouter(prefix="/model", tags=["model"])


@router.get("", response_model=ModelCardResponse, summary="Model card of the served model")
async def model_card(classifier: ClassifierDep) -> ModelCardResponse:
    return ModelCardResponse.from_card(classifier.model_card)
