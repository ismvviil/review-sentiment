"""Adapter implementing the ``SentimentPredictor`` port: embeddings + scikit-learn classifier."""

from collections.abc import Mapping, Sequence
from typing import Any

from review_sentiment.domain.model_card import ModelCard
from review_sentiment.domain.sentiment import Sentiment
from review_sentiment.ml.artifacts import ArtifactStore
from review_sentiment.ml.encoders import TextEncoder, build_encoder, with_runtime


class EmbeddingSentimentPredictor:
    def __init__(self, encoder: TextEncoder, classifier: Any, card: ModelCard) -> None:
        self._encoder = encoder
        self._classifier = classifier
        self._card = card
        self._labels = [Sentiment(str(c)) for c in classifier.classes_]

    @property
    def card(self) -> ModelCard:
        return self._card

    def predict_scores(self, texts: Sequence[str]) -> list[Mapping[Sentiment, float]]:
        vectors = self._encoder.encode(texts)
        probabilities = self._classifier.predict_proba(vectors)
        return [dict(zip(self._labels, map(float, row), strict=True)) for row in probabilities]


def load_predictor(
    store: ArtifactStore, version: str = "latest", runtime: str = "auto"
) -> EmbeddingSentimentPredictor:
    """Build a ready predictor from a stored artifact (the encoder comes from its model card,
    optionally executed on an equivalent runtime such as ONNX)."""
    artifact = store.load(version)
    encoder = build_encoder(with_runtime(artifact.card.encoder, runtime))
    return EmbeddingSentimentPredictor(encoder, artifact.classifier, artifact.card)
