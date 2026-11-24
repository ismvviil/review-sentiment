"""
Datasets return a DataFrame with two columns: ``text`` and ``sentiment``
(``negative`` / ``neutral`` / ``positive``). How the raw labels are mapped is the dataset's job.

Extension point: add a module in this package with a class decorated with
``@dataset_registry.register("my-dataset")`` and reference it in ``configs/training.toml``.
"""

from collections.abc import Callable
from typing import Any, Protocol

import pandas as pd

from review_sentiment.core.registry import Registry, import_submodules


class DatasetLoader(Protocol):
    def load(self) -> pd.DataFrame: ...

    def describe(self) -> dict[str, Any]:
        """Short description stored in the model card."""
        ...


dataset_registry: Registry[Callable[..., DatasetLoader]] = Registry("dataset")


def build_dataset(spec: dict[str, Any], *, seed: int) -> DatasetLoader:
    import_submodules(__package__)
    params = dict(spec)
    return dataset_registry.get(params.pop("type"))(seed=seed, **params)
