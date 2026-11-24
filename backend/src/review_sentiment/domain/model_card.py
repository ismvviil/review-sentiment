"""
Model Card: the description of a trained model (what it is, how it was trained, how well it
performs). Written by the training pipeline next to the model file, read by the API.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# metrics[classifier_name][split_name][metric_name] -> value
Metrics = dict[str, dict[str, dict[str, float]]]


@dataclass(frozen=True)
class ModelCard:
    name: str
    version: str
    created_at: str
    classifier: str
    encoder: dict[str, Any]          # e.g. {"type": "sentence-transformer", "model_name": "..."}
    dataset: dict[str, Any]          # e.g. {"name": "...", "samples_per_class": 6000}
    labels: list[str]
    train_size: int
    test_size: int
    selection_metric: str
    metrics: Metrics = field(default_factory=dict)
    confusion_matrix: list[list[int]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelCard:
        known = cls.__dataclass_fields__.keys()
        return cls(**{k: v for k, v in data.items() if k in known})
