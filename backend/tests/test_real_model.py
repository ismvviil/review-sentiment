"""End-to-end check with the real trained model (skipped if no model has been trained)."""

import pytest

from review_sentiment.api.container import build_review_classifier
from review_sentiment.core.config import Settings
from review_sentiment.domain.sentiment import Sentiment
from review_sentiment.ml.artifacts import ArtifactStore

settings = Settings()
has_model = bool(ArtifactStore(settings.artifacts_dir, settings.model_name).versions())

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not has_model, reason="no trained model, run the training first"),
]


@pytest.fixture(scope="module")
def classifier():
    return build_review_classifier(settings)


@pytest.mark.parametrize(("review", "expected"), [
    ("Absolutely love it, works perfectly and arrived early!", Sentiment.POSITIVE),
    ("Stopped working after two days. Total waste of money.", Sentiment.NEGATIVE),
])
def test_obvious_reviews(classifier, review, expected):
    assert classifier.classify(review) is expected
