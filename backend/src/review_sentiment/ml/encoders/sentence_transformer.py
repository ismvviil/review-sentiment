from collections.abc import Sequence
from typing import Any

import numpy as np

from review_sentiment.ml.encoders.base import encoder_registry


@encoder_registry.register("sentence-transformer")
class SentenceTransformerEncoder:
    """Adapter around the sentence-transformers library (e.g. all-MiniLM-L6-v2, 384-d)."""

    def __init__(
        self,
        model_name: str,
        batch_size: int = 64,
        normalize: bool = True,
        dimension: int | None = None,
    ) -> None:
        # Imported lazily: torch is heavy and not needed by code that never encodes
        from sentence_transformers import SentenceTransformer

        self._model_name = model_name
        self._batch_size = batch_size
        self._normalize = normalize
        self._model = SentenceTransformer(model_name)
        get_dim = (getattr(self._model, "get_embedding_dimension", None)
                   or self._model.get_sentence_embedding_dimension)
        actual = self._dimension = get_dim()
        if dimension is not None and dimension != actual:
            raise ValueError(f"{model_name} produces {actual}-d vectors, expected {dimension}")

    @property
    def spec(self) -> dict[str, Any]:
        return {
            "type": "sentence-transformer",
            "model_name": self._model_name,
            "normalize": self._normalize,
            "dimension": self._dimension,
        }

    def encode(self, texts: Sequence[str], *, show_progress: bool = False) -> np.ndarray:
        return self._model.encode(
            list(texts),
            batch_size=self._batch_size,
            normalize_embeddings=self._normalize,
            convert_to_numpy=True,
            show_progress_bar=show_progress,
        )
