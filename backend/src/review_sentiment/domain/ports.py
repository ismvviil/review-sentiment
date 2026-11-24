"""
Ports (Hexagonal Architecture): interfaces the application needs, implemented by adapters
in the infrastructure (``ml``) layer. The application depends on these abstractions,
never on sentence-transformers or scikit-learn directly (Dependency Inversion).
"""

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from review_sentiment.domain.model_card import ModelCard
from review_sentiment.domain.sentiment import Sentiment


@runtime_checkable
class SentimentPredictor(Protocol):
    """Anything that turns texts into a probability per sentiment."""

    @property
    def card(self) -> ModelCard: ...

    def predict_scores(self, texts: Sequence[str]) -> list[Mapping[Sentiment, float]]: ...
