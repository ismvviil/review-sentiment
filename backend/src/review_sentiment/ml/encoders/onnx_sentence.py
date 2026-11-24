"""
Same sentence-transformer model, executed with ONNX Runtime instead of PyTorch.

Reproduces the sentence-transformers pipeline (tokenize -> transformer -> mean pooling ->
L2 normalize) with ~5x less memory and no torch dependency, which makes the API fit on
small cloud instances (512 MB). Produces the same vectors, so a classifier trained on
PyTorch embeddings can be served with this encoder (see ``encoder_runtime`` setting).
"""

import json
import os
from collections.abc import Sequence
from typing import Any

import numpy as np

from review_sentiment.ml.encoders.base import encoder_registry


@encoder_registry.register("sentence-transformer-onnx")
class OnnxSentenceEncoder:
    def __init__(
        self,
        model_name: str,
        batch_size: int = 8,  # small chunks keep peak memory low on 512 MB instances
        normalize: bool = True,
        dimension: int | None = None,
        onnx_file: str = "onnx/model.onnx",
    ) -> None:
        # Imported lazily so the package imports fine without the "onnx" extra installed
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        from tokenizers import Tokenizer

        self._model_name = model_name
        self._batch_size = batch_size
        self._normalize = normalize

        # Same max length as sentence-transformers uses for this model
        config_path = hf_hub_download(model_name, "sentence_bert_config.json")
        with open(config_path, encoding="utf-8") as f:
            max_len = json.load(f).get("max_seq_length", 256)

        self._tokenizer = Tokenizer.from_file(hf_hub_download(model_name, "tokenizer.json"))
        self._tokenizer.enable_truncation(max_length=max_len)
        self._tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

        options = ort.SessionOptions()
        options.intra_op_num_threads = int(os.getenv("ORT_THREADS", "0"))  # 0 = all cores
        # Give memory back after each batch instead of keeping a growing arena
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False
        self._session = ort.InferenceSession(
            hf_hub_download(model_name, onnx_file), options, providers=["CPUExecutionProvider"]
        )
        self._inputs = {i.name for i in self._session.get_inputs()}

        self._dimension = int(self.encode(["dimension probe"]).shape[1])
        if dimension is not None and dimension != self._dimension:
            raise ValueError(f"{model_name} produces {self._dimension}-d vectors, "
                             f"expected {dimension}")

    @property
    def spec(self) -> dict[str, Any]:
        return {
            "type": "sentence-transformer-onnx",
            "model_name": self._model_name,
            "normalize": self._normalize,
            "dimension": self._dimension,
        }

    def encode(self, texts: Sequence[str], *, show_progress: bool = False) -> np.ndarray:
        chunks = [self._encode_batch(list(texts[i:i + self._batch_size]))
                  for i in range(0, len(texts), self._batch_size)]
        return np.vstack(chunks) if chunks else np.empty((0, getattr(self, "_dimension", 0)))

    def _encode_batch(self, texts: list[str]) -> np.ndarray:
        encodings = self._tokenizer.encode_batch(texts)
        ids = np.array([e.ids for e in encodings], dtype=np.int64)
        mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
        feeds = {"input_ids": ids, "attention_mask": mask,
                 "token_type_ids": np.zeros_like(ids)}
        token_embeddings = self._session.run(None, {k: v for k, v in feeds.items()
                                                    if k in self._inputs})[0]

        # Mean pooling over real tokens (padding excluded)
        weights = mask[..., None].astype(np.float32)
        sentence = (token_embeddings * weights).sum(axis=1) / np.clip(weights.sum(axis=1), 1e-9, None)
        if self._normalize:
            sentence /= np.clip(np.linalg.norm(sentence, axis=1, keepdims=True), 1e-12, None)
        return sentence.astype(np.float32)
