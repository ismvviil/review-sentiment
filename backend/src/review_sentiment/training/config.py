from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from review_sentiment.core.config import BACKEND_ROOT

DEFAULT_CONFIG = BACKEND_ROOT / "configs" / "training.toml"


@dataclass(frozen=True)
class ClassifierConfig:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingConfig:
    model_name: str
    dataset: dict[str, Any]
    encoder: dict[str, Any]
    classifiers: list[ClassifierConfig]
    test_size: float = 0.2
    seed: int = 42
    selection_metric: str = "f1"

    @classmethod
    def from_toml(cls, path: Path = DEFAULT_CONFIG) -> TrainingConfig:
        raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            model_name=raw.get("model_name", "sentiment-classifier"),
            dataset=raw["dataset"],
            encoder=raw["encoder"],
            classifiers=[ClassifierConfig(**c) for c in raw["classifiers"]],
            test_size=raw.get("split", {}).get("test_size", 0.2),
            seed=raw.get("split", {}).get("seed", 42),
            selection_metric=raw.get("selection", {}).get("metric", "f1"),
        )
