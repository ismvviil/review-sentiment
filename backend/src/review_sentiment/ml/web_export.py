"""
Export the served model to JSON so it can run in a web browser (static hosting, no server).

The embedding model is the same MiniLM, loaded in the browser by transformers.js. The
classifier is linear, so it is exported as plain numbers + the formula family (``format``).

    python -m review_sentiment.ml.web_export --out ../frontend/public/model

Extension point: support another classifier type with ``@exporter_registry.register(Cls)``.
"""

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

from review_sentiment.core.config import get_settings
from review_sentiment.ml.artifacts import ArtifactStore

Exporter = Callable[[Any], dict[str, Any]]


class _ExporterRegistry:
    def __init__(self) -> None:
        self._items: dict[type, Exporter] = {}

    def register(self, cls: type) -> Callable[[Exporter], Exporter]:
        def decorator(fn: Exporter) -> Exporter:
            self._items[cls] = fn
            return fn
        return decorator

    def export(self, classifier: Any) -> dict[str, Any]:
        for cls, fn in self._items.items():
            if isinstance(classifier, cls):
                return {"labels": [str(c) for c in classifier.classes_], **fn(classifier)}
        raise TypeError(f"No web exporter for {type(classifier).__name__}")


exporter_registry = _ExporterRegistry()


def _linear(estimator: Any) -> dict[str, Any]:
    return {"coef": estimator.coef_.round(7).tolist(),
            "intercept": estimator.intercept_.round(7).tolist()}


@exporter_registry.register(LogisticRegression)
def export_logistic_regression(clf: LogisticRegression) -> dict[str, Any]:
    # p = softmax(coef @ x + intercept)
    return {"format": "softmax-linear", **_linear(clf)}


@exporter_registry.register(CalibratedClassifierCV)
def export_calibrated_linear(clf: CalibratedClassifierCV) -> dict[str, Any]:
    # per fold: f = coef @ x + b ; p_k = 1 / (1 + exp(a_k f_k + b_k)) ; p /= sum(p)
    # final probability = mean over folds
    if clf.method != "sigmoid":
        raise TypeError("Only sigmoid calibration is supported")
    return {
        "format": "calibrated-linear",
        "folds": [
            {**_linear(c.estimator),
             "calibrators": [{"a": float(cal.a_), "b": float(cal.b_)} for cal in c.calibrators]}
            for c in clf.calibrated_classifiers_
        ],
    }


def predict_proba(exported: dict[str, Any], x: np.ndarray) -> np.ndarray:
    """Reference implementation of the exported formulas (the JS code mirrors it)."""
    def linear(p):
        return x @ np.array(p["coef"]).T + np.array(p["intercept"])

    if exported["format"] == "softmax-linear":
        z = linear(exported)
        e = np.exp(z - z.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    folds = []
    for fold in exported["folds"]:
        f = linear(fold)
        a = np.array([c["a"] for c in fold["calibrators"]])
        b = np.array([c["b"] for c in fold["calibrators"]])
        p = 1.0 / (1.0 + np.exp(a * f + b))
        folds.append(p / p.sum(axis=1, keepdims=True))
    return np.mean(folds, axis=0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the served model for the browser.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--version", default="latest")
    args = parser.parse_args()

    settings = get_settings()
    artifact = ArtifactStore(settings.artifacts_dir, settings.model_name).load(args.version)
    exported = exporter_registry.export(artifact.classifier)

    # Self-check: the exported formula must reproduce scikit-learn's probabilities
    probe = np.random.default_rng(0).normal(size=(200, artifact.card.encoder["dimension"]))
    probe /= np.linalg.norm(probe, axis=1, keepdims=True)
    error = np.abs(predict_proba(exported, probe) - artifact.classifier.predict_proba(probe)).max()
    if error > 1e-5:
        raise RuntimeError(f"Exported model differs from scikit-learn (max error {error:.2e})")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "classifier.json").write_text(json.dumps(exported), encoding="utf-8")
    (args.out / "model_card.json").write_text(
        json.dumps(artifact.card.to_dict(), indent=2), encoding="utf-8")
    print(f"Exported {artifact.card.classifier} v{artifact.card.version} -> {args.out} "
          f"(format {exported['format']}, max error vs scikit-learn {error:.1e})")


if __name__ == "__main__":
    main()
