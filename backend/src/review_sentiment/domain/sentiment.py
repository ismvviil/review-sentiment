"""Core domain objects. Pure Python: no framework, no ML library."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from review_sentiment.domain.errors import InvalidReviewError


class Sentiment(StrEnum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


@dataclass(frozen=True, slots=True)
class Review:
    """A review text that is guaranteed to be valid (Value Object)."""

    text: str

    @classmethod
    def create(cls, raw: str, max_chars: int) -> Review:
        text = " ".join(str(raw).split())  # collapse whitespace and newlines
        if not text:
            raise InvalidReviewError("The review is empty.")
        if len(text) > max_chars:
            raise InvalidReviewError(f"The review is too long (max {max_chars} characters).")
        return cls(text)


@dataclass(frozen=True, slots=True)
class Prediction:
    """The outcome of classifying one review."""

    sentiment: Sentiment
    confidence: float
    scores: Mapping[Sentiment, float] = field(default_factory=dict)

    @classmethod
    def from_scores(cls, scores: Mapping[Sentiment, float]) -> Prediction:
        """The predicted sentiment is the class with the highest probability."""
        if not scores:
            raise ValueError("Cannot build a prediction from empty scores")
        rounded = {label: round(float(p), 4) for label, p in scores.items()}
        best = max(rounded, key=rounded.__getitem__)
        return cls(sentiment=best, confidence=rounded[best], scores=rounded)
