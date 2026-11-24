from collections.abc import Mapping, Sequence

import pytest
from fastapi.testclient import TestClient

from review_sentiment.api.app import create_app
from review_sentiment.application.review_classifier import ReviewClassifier
from review_sentiment.core.config import Settings
from review_sentiment.domain.errors import ModelNotAvailableError
from review_sentiment.domain.model_card import ModelCard
from review_sentiment.domain.sentiment import Sentiment

FAKE_CARD = ModelCard(
    name="fake", version="test", created_at="2026-01-01T00:00:00", classifier="keyword-fake",
    encoder={"type": "none"}, dataset={"name": "unit-tests"},
    labels=["negative", "neutral", "positive"], train_size=0, test_size=0,
    selection_metric="f1",
)


class FakePredictor:
    """Deterministic stand-in for the ML model (implements the SentimentPredictor port)."""

    card = FAKE_CARD

    def predict_scores(self, texts: Sequence[str]) -> list[Mapping[Sentiment, float]]:
        def score(text: str) -> dict[Sentiment, float]:
            t = text.lower()
            if "love" in t or "great" in t:
                return {Sentiment.NEGATIVE: 0.05, Sentiment.NEUTRAL: 0.15, Sentiment.POSITIVE: 0.8}
            if "broke" in t or "terrible" in t:
                return {Sentiment.NEGATIVE: 0.9, Sentiment.NEUTRAL: 0.08, Sentiment.POSITIVE: 0.02}
            return {Sentiment.NEGATIVE: 0.2, Sentiment.NEUTRAL: 0.6, Sentiment.POSITIVE: 0.2}

        return [score(t) for t in texts]


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", max_review_chars=200, max_batch_size=3,
                    log_level="WARNING")


@pytest.fixture
def classifier(settings: Settings) -> ReviewClassifier:
    return ReviewClassifier(FakePredictor(), max_chars=settings.max_review_chars,
                            max_batch=settings.max_batch_size)


@pytest.fixture
def client(settings: Settings, classifier: ReviewClassifier):
    app = create_app(settings, classifier_factory=lambda _: classifier)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def client_without_model(settings: Settings):
    def failing_factory(_):
        raise ModelNotAvailableError("No trained model.")

    app = create_app(settings, classifier_factory=failing_factory)
    with TestClient(app) as c:
        yield c
