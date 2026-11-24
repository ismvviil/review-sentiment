import pytest

from review_sentiment.domain.errors import InvalidReviewError
from review_sentiment.domain.sentiment import Prediction, Review, Sentiment


class TestReview:
    def test_normalizes_whitespace(self):
        assert Review.create("  Great \n\n product  ", max_chars=100).text == "Great product"

    @pytest.mark.parametrize("raw", ["", "   ", "\n\t"])
    def test_rejects_empty(self, raw):
        with pytest.raises(InvalidReviewError, match="empty"):
            Review.create(raw, max_chars=100)

    def test_rejects_too_long(self):
        with pytest.raises(InvalidReviewError, match="too long"):
            Review.create("a" * 11, max_chars=10)


class TestPrediction:
    def test_picks_highest_score(self):
        p = Prediction.from_scores({Sentiment.NEGATIVE: 0.1, Sentiment.NEUTRAL: 0.3,
                                    Sentiment.POSITIVE: 0.6})
        assert p.sentiment is Sentiment.POSITIVE
        assert p.confidence == 0.6

    def test_rounds_scores(self):
        p = Prediction.from_scores({Sentiment.NEGATIVE: 0.123456, Sentiment.POSITIVE: 0.876544})
        assert p.scores[Sentiment.NEGATIVE] == 0.1235

    def test_rejects_empty_scores(self):
        with pytest.raises(ValueError):
            Prediction.from_scores({})
