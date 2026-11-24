"""
Decorator pattern: wraps any TextEncoder and caches its vectors on disk.

Encoding is by far the slowest step of training (minutes on a laptop CPU). The cache key is
a hash of the encoder spec + the exact texts, so a cached file can never be reused for
different data or a different model.
"""

import hashlib
import json
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from review_sentiment.ml.encoders import TextEncoder

logger = logging.getLogger(__name__)


class CachedEncoder:
    def __init__(self, inner: TextEncoder, cache_dir: Path) -> None:
        self._inner = inner
        self._cache_dir = Path(cache_dir)

    @property
    def spec(self) -> dict[str, Any]:
        return self._inner.spec

    def cache_key(self, texts: Sequence[str]) -> str:
        digest = hashlib.sha256(json.dumps(self.spec, sort_keys=True).encode())
        for text in texts:
            digest.update(text.encode("utf-8"))
            digest.update(b"\x00")
        return digest.hexdigest()[:20]

    def encode(self, texts: Sequence[str], *, show_progress: bool = False) -> np.ndarray:
        path = self._cache_dir / f"{self.cache_key(texts)}.npy"
        if path.exists():
            logger.info("Embeddings cache hit (%d texts) -> %s", len(texts), path.name)
            return np.load(path)

        vectors = self._inner.encode(texts, show_progress=show_progress)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        np.save(path, vectors)
        return vectors
