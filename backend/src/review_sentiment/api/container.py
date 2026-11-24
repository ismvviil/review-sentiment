"""
Composition root: the single place where concrete classes are chosen and wired together.
Everything else receives its dependencies (Dependency Injection), so tests can swap the
real model for a fake one by passing another ``ClassifierFactory`` to ``create_app``.
"""

from collections.abc import Callable
from dataclasses import dataclass

from review_sentiment.application.review_classifier import ReviewClassifier
from review_sentiment.core.config import Settings
from review_sentiment.ml.artifacts import ArtifactStore
from review_sentiment.ml.predictor import load_predictor

ClassifierFactory = Callable[[Settings], ReviewClassifier]


@dataclass
class Container:
    settings: Settings
    classifier: ReviewClassifier | None = None
    startup_error: str | None = None

    @property
    def ready(self) -> bool:
        return self.classifier is not None


def build_review_classifier(settings: Settings) -> ReviewClassifier:
    store = ArtifactStore(settings.artifacts_dir, settings.model_name)
    predictor = load_predictor(store, settings.model_version, settings.encoder_runtime)
    return ReviewClassifier(
        predictor, max_chars=settings.max_review_chars, max_batch=settings.max_batch_size
    )
