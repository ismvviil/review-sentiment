"""
Text encoders turn texts into vectors (embeddings).

The encoder used at training time is described in the model card (``spec``) and rebuilt
from it at serving time - so training and serving can never drift apart.

Extension point: add a module in this package with a class decorated with
``@encoder_registry.register("my-encoder")``. It is discovered automatically.
"""

import importlib.util
from collections.abc import Callable, Sequence
from typing import Any, Protocol

import numpy as np

from review_sentiment.core.registry import Registry, import_submodules


class TextEncoder(Protocol):
    @property
    def spec(self) -> dict[str, Any]:
        """Serializable description, enough to rebuild the same encoder."""
        ...

    def encode(self, texts: Sequence[str], *, show_progress: bool = False) -> np.ndarray: ...


encoder_registry: Registry[Callable[..., TextEncoder]] = Registry("encoder")

# Encoders that compute the *same* vectors with another runtime: {runtime: {type: equivalent}}
RUNTIME_EQUIVALENTS: dict[str, dict[str, str]] = {
    "onnx": {"sentence-transformer": "sentence-transformer-onnx"},
}


def with_runtime(spec: dict[str, Any], runtime: str = "auto") -> dict[str, Any]:
    """Swap an encoder for an equivalent one on another runtime (e.g. PyTorch -> ONNX).

    ``auto`` keeps PyTorch when it is installed and falls back to ONNX otherwise.
    """
    if runtime == "auto":
        runtime = "torch" if importlib.util.find_spec("sentence_transformers") else "onnx"
    equivalent = RUNTIME_EQUIVALENTS.get(runtime, {}).get(spec["type"])
    return {**spec, "type": equivalent} if equivalent else dict(spec)


def build_encoder(spec: dict[str, Any]) -> TextEncoder:
    """Factory: ``{"type": "sentence-transformer", "model_name": "..."}`` -> encoder."""
    import_submodules(__package__)
    params = dict(spec)
    encoder_type = params.pop("type")
    return encoder_registry.get(encoder_type)(**params)
