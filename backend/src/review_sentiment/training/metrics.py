"""
Evaluation metrics (macro-averaged: every sentiment class counts equally).

Extension point: ``metric_registry.register("cohen-kappa")(cohen_kappa_score)``.
"""

from collections.abc import Callable, Sequence
from functools import partial

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from review_sentiment.core.registry import Registry

MetricFn = Callable[[Sequence[str], Sequence[str]], float]

metric_registry: Registry[MetricFn] = Registry("metric")
metric_registry.register("accuracy")(accuracy_score)
metric_registry.register("precision")(partial(precision_score, average="macro", zero_division=0))
metric_registry.register("recall")(partial(recall_score, average="macro", zero_division=0))
metric_registry.register("f1")(partial(f1_score, average="macro", zero_division=0))


def compute_metrics(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, float]:
    return {name: round(float(metric_registry.get(name)(y_true, y_pred)), 4)
            for name in metric_registry}
