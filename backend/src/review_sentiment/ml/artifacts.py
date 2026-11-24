"""
Versioned model storage (Repository pattern).

    artifacts/
    └── sentiment-classifier/
        ├── LATEST                      <- name of the current version
        └── 20261124-093100/
            ├── classifier.joblib       <- fitted scikit-learn classifier
            └── model_card.json         <- how it was trained + its metrics

Every training run creates a new version; the API serves ``LATEST`` unless a version is
pinned with ``SENTIMENT_MODEL_VERSION``. Rolling back = pointing to an older folder.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from review_sentiment.domain.errors import ModelNotAvailableError
from review_sentiment.domain.model_card import ModelCard

CLASSIFIER_FILE = "classifier.joblib"
CARD_FILE = "model_card.json"
LATEST_FILE = "LATEST"


@dataclass(frozen=True)
class ModelArtifact:
    classifier: Any
    card: ModelCard


class ArtifactStore:
    def __init__(self, root: Path, model_name: str) -> None:
        self._dir = Path(root) / model_name

    @property
    def directory(self) -> Path:
        return self._dir

    def save(self, classifier: Any, card: ModelCard) -> Path:
        target = self._dir / card.version
        target.mkdir(parents=True, exist_ok=False)
        joblib.dump(classifier, target / CLASSIFIER_FILE)
        (target / CARD_FILE).write_text(json.dumps(card.to_dict(), indent=2), encoding="utf-8")
        (self._dir / LATEST_FILE).write_text(card.version, encoding="utf-8")
        return target

    def load(self, version: str = "latest") -> ModelArtifact:
        folder = self._dir / self.resolve(version)
        if not (folder / CLASSIFIER_FILE).exists():
            raise ModelNotAvailableError(f"No model found in {folder}.")
        card = ModelCard.from_dict(json.loads((folder / CARD_FILE).read_text(encoding="utf-8")))
        return ModelArtifact(classifier=joblib.load(folder / CLASSIFIER_FILE), card=card)

    def resolve(self, version: str) -> str:
        if version != "latest":
            return version
        latest = self._dir / LATEST_FILE
        if not latest.exists():
            raise ModelNotAvailableError(
                f"No trained model in {self._dir}. Run the training first: "
                "python -m review_sentiment.training"
            )
        return latest.read_text(encoding="utf-8").strip()

    def versions(self) -> list[str]:
        if not self._dir.exists():
            return []
        return sorted(p.name for p in self._dir.iterdir() if (p / CARD_FILE).exists())
