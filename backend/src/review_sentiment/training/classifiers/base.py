"""
Classifier factories (Factory + Registry).

Every classifier must expose ``predict_proba`` - the API returns a probability per sentiment.

Extension point: add a module in this package, e.g. ``knn.py``::

    @classifier_registry.register("knn")
    def knn(**params):
        return KNeighborsClassifier(**{"n_neighbors": 15, **params})

then list ``name = "knn"`` under ``[[classifiers]]`` in ``configs/training.toml``.
"""

from collections.abc import Callable
from typing import Any

from review_sentiment.core.registry import Registry, import_submodules

classifier_registry: Registry[Callable[..., Any]] = Registry("classifier")


def build_classifier(name: str, params: dict[str, Any] | None = None, *, seed: int = 42) -> Any:
    import_submodules(__package__)
    classifier = classifier_registry.get(name)(seed=seed, **(params or {}))
    if not hasattr(classifier, "predict_proba"):
        raise TypeError(f"Classifier '{name}' must implement predict_proba")
    return classifier
