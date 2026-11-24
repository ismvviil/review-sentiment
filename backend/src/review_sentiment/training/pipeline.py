"""
Stage 1 - the training pipeline (Template Method: the steps are fixed, every step's
implementation comes from a plugin chosen in the config).

    dataset -> train/test split -> encoder (embeddings) -> classifiers -> metrics
            -> best classifier -> versioned artifact + model card
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from review_sentiment.domain.model_card import Metrics, ModelCard
from review_sentiment.ml.artifacts import ArtifactStore
from review_sentiment.ml.encoders import TextEncoder, build_encoder
from review_sentiment.training.classifiers import build_classifier
from review_sentiment.training.config import TrainingConfig
from review_sentiment.training.datasets import build_dataset
from review_sentiment.training.metrics import compute_metrics
from review_sentiment.training.reporting import TrainingObserver

EncoderFactory = Callable[[dict[str, Any]], TextEncoder]


@dataclass(frozen=True)
class TrainingResult:
    card: ModelCard
    artifact_path: Path
    classification_report: str


class TrainingPipeline:
    def __init__(
        self,
        config: TrainingConfig,
        store: ArtifactStore,
        *,
        encoder_factory: EncoderFactory = build_encoder,
        observers: Sequence[TrainingObserver] = (),
    ) -> None:
        self._config = config
        self._store = store
        self._encoder_factory = encoder_factory
        self._observers = list(observers)

    def run(self) -> TrainingResult:
        cfg = self._config

        # 1. Data
        self._step(f"Loading dataset '{cfg.dataset['type']}'")
        dataset = build_dataset(cfg.dataset, seed=cfg.seed)
        df = dataset.load()
        counts = df["sentiment"].value_counts().to_dict()
        self._step(f"{len(df)} reviews: {counts}")

        # 2. Split (stratified: same class proportions in train and test)
        x_train_txt, x_test_txt, y_train, y_test = train_test_split(
            df["text"].tolist(), df["sentiment"].tolist(),
            test_size=cfg.test_size, random_state=cfg.seed, stratify=df["sentiment"],
        )
        self._step(f"Split: {len(x_train_txt)} train / {len(x_test_txt)} test")

        # 3. Embeddings
        self._step(f"Encoding with {cfg.encoder.get('model_name', cfg.encoder['type'])}")
        encoder = self._encoder_factory(cfg.encoder)
        x_train = encoder.encode(x_train_txt, show_progress=True)
        x_test = encoder.encode(x_test_txt, show_progress=True)

        # 4. Train + evaluate every configured classifier, on train AND test
        metrics: Metrics = {}
        fitted: dict[str, Any] = {}
        for clf_cfg in cfg.classifiers:
            self._step(f"Training {clf_cfg.name}")
            clf = build_classifier(clf_cfg.name, clf_cfg.params, seed=cfg.seed)
            clf.fit(x_train, y_train)
            fitted[clf_cfg.name] = clf
            metrics[clf_cfg.name] = {
                "train": compute_metrics(y_train, clf.predict(x_train)),
                "test": compute_metrics(y_test, clf.predict(x_test)),
            }
            for observer in self._observers:
                observer.on_classifier_evaluated(clf_cfg.name, metrics[clf_cfg.name])

        # 5. Model selection on the TEST set
        best_name = max(metrics, key=lambda n: metrics[n]["test"][cfg.selection_metric])
        best = fitted[best_name]
        y_pred = best.predict(x_test)
        labels = [str(c) for c in best.classes_]

        # 6. Persist a new version with its model card
        now = datetime.now().astimezone()
        card = ModelCard(
            name=cfg.model_name,
            version=now.strftime("%Y%m%d-%H%M%S"),
            created_at=now.isoformat(timespec="seconds"),
            classifier=best_name,
            encoder=encoder.spec,
            dataset=dataset.describe(),
            labels=labels,
            train_size=len(x_train_txt),
            test_size=len(x_test_txt),
            selection_metric=cfg.selection_metric,
            metrics=metrics,
            confusion_matrix=confusion_matrix(y_test, y_pred, labels=labels).tolist(),
        )
        result = TrainingResult(
            card=card,
            artifact_path=self._store.save(best, card),
            classification_report=classification_report(y_test, y_pred, digits=4),
        )
        for observer in self._observers:
            observer.on_completed(result)
        return result

    def _step(self, message: str) -> None:
        for observer in self._observers:
            observer.on_step(message)
