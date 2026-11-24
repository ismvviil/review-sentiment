import numpy as np
import pytest

from review_sentiment.ml.web_export import exporter_registry, predict_proba
from review_sentiment.training.classifiers import build_classifier

rng = np.random.default_rng(0)
X = rng.normal(size=(150, 16))
X /= np.linalg.norm(X, axis=1, keepdims=True)
y = np.array(["negative", "neutral", "positive"])[rng.integers(0, 3, size=150)]


@pytest.mark.parametrize("name", ["logistic-regression", "linear-svm"])
def test_exported_formula_matches_scikit_learn(name):
    clf = build_classifier(name, {}, seed=0).fit(X, y)
    exported = exporter_registry.export(clf)
    assert exported["labels"] == ["negative", "neutral", "positive"]
    assert np.abs(predict_proba(exported, X) - clf.predict_proba(X)).max() < 1e-5


def test_unsupported_classifier_is_rejected():
    clf = build_classifier("random-forest", {"n_estimators": 5}, seed=0).fit(X, y)
    with pytest.raises(TypeError, match="No web exporter"):
        exporter_registry.export(clf)
