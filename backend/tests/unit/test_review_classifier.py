import pytest

from review_sentiment.domain.errors import BatchTooLargeError, InvalidReviewError
from review_sentiment.domain.sentiment import Sentiment


def test_classify_returns_a_sentiment(classifier):
    assert classifier.classify("I love it") is Sentiment.POSITIVE
    assert classifier.classify("It broke on day one") is Sentiment.NEGATIVE
    assert classifier.classify("It is a product") is Sentiment.NEUTRAL


def test_predict_includes_all_scores(classifier):
    prediction = classifier.predict("great value")
    assert set(prediction.scores) == set(Sentiment)
    assert prediction.confidence == max(prediction.scores.values())


def test_predict_many_keeps_order(classifier):
    results = classifier.predict_many(["great", "terrible", "ok"])
    assert [r.sentiment for r in results] == [Sentiment.POSITIVE, Sentiment.NEGATIVE,
                                              Sentiment.NEUTRAL]


def test_rejects_invalid_review(classifier):
    with pytest.raises(InvalidReviewError):
        classifier.classify("   ")


def test_rejects_batch_over_limit(classifier):
    with pytest.raises(BatchTooLargeError):
        classifier.predict_many(["a", "b", "c", "d"])
