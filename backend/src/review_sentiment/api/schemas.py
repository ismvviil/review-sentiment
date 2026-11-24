"""DTOs: the public JSON contract of the API, validated by Pydantic."""

from collections import Counter
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from review_sentiment.domain.model_card import ModelCard
from review_sentiment.domain.sentiment import Prediction, Sentiment


class ClassifyRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [{"review": "The blender is powerful and very easy to clean."}]
    })
    review: str = Field(min_length=1, description="The product review to classify")


class BatchClassifyRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [{"reviews": ["Great quality!", "It's okay.", "Broke after one use."]}]
    })
    reviews: list[str] = Field(min_length=1, description="Reviews to classify in one call")


class ClassificationResponse(BaseModel):
    review: str
    sentiment: Sentiment
    confidence: float = Field(ge=0, le=1)
    scores: dict[Sentiment, float]

    @classmethod
    def from_prediction(cls, review: str, prediction: Prediction) -> "ClassificationResponse":
        return cls(review=review, sentiment=prediction.sentiment,
                   confidence=prediction.confidence, scores=dict(prediction.scores))


class BatchClassificationResponse(BaseModel):
    results: list[ClassificationResponse]
    summary: dict[Sentiment, int] = Field(description="Number of reviews per sentiment")

    @classmethod
    def build(cls, results: list[ClassificationResponse]) -> "BatchClassificationResponse":
        counts = Counter(r.sentiment for r in results)
        return cls(results=results, summary={s: counts.get(s, 0) for s in Sentiment})


class ModelCardResponse(BaseModel):
    name: str
    version: str
    created_at: str
    classifier: str
    encoder: dict[str, Any]
    dataset: dict[str, Any]
    labels: list[str]
    train_size: int
    test_size: int
    selection_metric: str
    metrics: dict[str, dict[str, dict[str, float]]]
    confusion_matrix: list[list[int]]

    @classmethod
    def from_card(cls, card: ModelCard) -> "ModelCardResponse":
        return cls(**card.to_dict())


class HealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    version: str
    model_version: str | None = None
    detail: str | None = None
