from pathlib import Path
from typing import Any

import pandas as pd

from review_sentiment.core.config import BACKEND_ROOT
from review_sentiment.domain.sentiment import Sentiment
from review_sentiment.training.datasets.base import dataset_registry

SOURCE_URL = (
    "https://huggingface.co/datasets/mteb/amazon_reviews_multi/resolve/main/en/train.jsonl"
)

# label = number of stars - 1
STARS_TO_SENTIMENT = {
    0: Sentiment.NEGATIVE.value,
    1: Sentiment.NEGATIVE.value,
    2: Sentiment.NEUTRAL.value,
    3: Sentiment.POSITIVE.value,
    4: Sentiment.POSITIVE.value,
}


@dataset_registry.register("amazon-reviews-multi")
class AmazonReviewsMulti:
    """Amazon product reviews (English), 200,000 reviews rated 1 to 5 stars."""

    def __init__(self, path: str, samples_per_class: int | None = None, seed: int = 42) -> None:
        self._path = Path(path) if Path(path).is_absolute() else BACKEND_ROOT / path
        self._samples_per_class = samples_per_class
        self._seed = seed

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self._path}\nDownload it with:\n"
                f'  curl -L -o "{self._path}" {SOURCE_URL}'
            )
        df = pd.read_json(self._path, lines=True)[["text", "label"]].dropna()
        df["sentiment"] = df["label"].map(STARS_TO_SENTIMENT)
        if self._samples_per_class:
            df = (
                df.groupby("sentiment")
                .sample(n=self._samples_per_class, random_state=self._seed)
                .reset_index(drop=True)
            )
        return df[["text", "sentiment"]]

    def describe(self) -> dict[str, Any]:
        return {
            "name": "mteb/amazon_reviews_multi (en)",
            "source": SOURCE_URL,
            "samples_per_class": self._samples_per_class,
            "label_mapping": "1-2 stars: negative, 3 stars: neutral, 4-5 stars: positive",
        }
