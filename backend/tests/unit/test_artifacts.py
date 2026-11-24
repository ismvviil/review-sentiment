import pytest
from sklearn.dummy import DummyClassifier

from review_sentiment.domain.errors import ModelNotAvailableError
from review_sentiment.ml.artifacts import ArtifactStore
from tests.conftest import FAKE_CARD


def test_save_then_load_latest(tmp_path):
    store = ArtifactStore(tmp_path, "demo")
    clf = DummyClassifier().fit([[0], [1]], ["neg", "pos"])
    store.save(clf, FAKE_CARD)

    artifact = store.load()
    assert artifact.card == FAKE_CARD
    assert list(artifact.classifier.classes_) == ["neg", "pos"]
    assert store.versions() == [FAKE_CARD.version]


def test_load_without_model_raises(tmp_path):
    with pytest.raises(ModelNotAvailableError, match="Run the training"):
        ArtifactStore(tmp_path, "demo").load()
