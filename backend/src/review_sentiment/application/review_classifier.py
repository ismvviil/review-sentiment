"""
Application layer (use case): classify reviews.

``ReviewClassifier.classify(review: str) -> Sentiment`` is the entry point required by the
assignment. It enforces the business rules (valid text, batch size) and delegates the
actual prediction to any ``SentimentPredictor`` it receives by dependency injection.
"""

from collections.abc import Sequence

from review_sentiment.domain.errors import BatchTooLargeError
from review_sentiment.domain.model_card import ModelCard
from review_sentiment.domain.ports import SentimentPredictor
from review_sentiment.domain.sentiment import Prediction, Review, Sentiment


class ReviewClassifier:
    def __init__(
        self, predictor: SentimentPredictor, *, max_chars: int = 5000, max_batch: int = 100
    ) -> None:
        self._predictor = predictor
        self._max_chars = max_chars
        self._max_batch = max_batch

    @property
    def model_card(self) -> ModelCard:
        return self._predictor.card

    def classify(self, review: str) -> Sentiment:
        """Return the sentiment of one review."""
        return self.predict(review).sentiment

    def predict(self, review: str) -> Prediction:
        """Return the sentiment of one review with the probability of each class."""
        return self.predict_many([review])[0]

    def predict_many(self, reviews: Sequence[str]) -> list[Prediction]:
        if len(reviews) > self._max_batch:
            raise BatchTooLargeError(f"At most {self._max_batch} reviews per batch.")
        texts = [Review.create(r, self._max_chars).text for r in reviews]
        return [Prediction.from_scores(s) for s in self._predictor.predict_scores(texts)]
