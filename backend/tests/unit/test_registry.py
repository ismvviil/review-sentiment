import pytest

from review_sentiment.core.registry import Registry
from review_sentiment.training.classifiers import build_classifier, classifier_registry
from review_sentiment.training.metrics import compute_metrics


def test_register_and_get():
    registry: Registry[int] = Registry("number")
    registry.register("one")(1)
    assert registry.get("one") == 1
    assert "one" in registry


def test_duplicate_name_is_rejected():
    registry: Registry[int] = Registry("number")
    registry.register("one")(1)
    with pytest.raises(ValueError):
        registry.register("one")(2)


def test_unknown_name_lists_available_items():
    registry: Registry[int] = Registry("number")
    registry.register("one")(1)
    with pytest.raises(KeyError, match="Available: one"):
        registry.get("two")


@pytest.mark.parametrize("name", ["logistic-regression", "random-forest", "linear-svm"])
def test_builtin_classifiers_are_discovered_and_probabilistic(name):
    clf = build_classifier(name, {}, seed=0)
    assert hasattr(clf, "predict_proba")
    assert name in classifier_registry


def test_compute_metrics():
    metrics = compute_metrics(["pos", "neg", "pos"], ["pos", "neg", "neg"])
    assert list(metrics) == ["accuracy", "precision", "recall", "f1"]
    assert metrics["accuracy"] == pytest.approx(0.6667, abs=1e-4)


def test_with_runtime_swaps_to_equivalent_onnx_encoder():
    from review_sentiment.ml.encoders import with_runtime

    spec = {"type": "sentence-transformer", "model_name": "m", "dimension": 384}
    assert with_runtime(spec, "onnx") == {**spec, "type": "sentence-transformer-onnx"}
    assert with_runtime(spec, "torch") == spec
    assert with_runtime({"type": "other"}, "onnx") == {"type": "other"}
