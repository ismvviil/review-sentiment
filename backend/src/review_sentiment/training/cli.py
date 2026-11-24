"""
Command line entry point (composition root of the training side).

    python -m review_sentiment.training                     # uses configs/training.toml
    python -m review_sentiment.training --config my.toml --no-cache
"""

import argparse
from pathlib import Path

from review_sentiment.core.config import BACKEND_ROOT, get_settings
from review_sentiment.core.logging import configure_logging
from review_sentiment.ml.artifacts import ArtifactStore
from review_sentiment.ml.encoders import build_encoder
from review_sentiment.training.config import DEFAULT_CONFIG, TrainingConfig
from review_sentiment.training.embedding_cache import CachedEncoder
from review_sentiment.training.pipeline import TrainingPipeline
from review_sentiment.training.reporting import LoggingObserver, ReportFileObserver

CACHE_DIR = BACKEND_ROOT / ".cache" / "embeddings"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train the review sentiment classifier.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--no-cache", action="store_true", help="always re-encode the texts")
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings.log_level)
    config = TrainingConfig.from_toml(args.config)

    def encoder_factory(spec):
        encoder = build_encoder(spec)
        return encoder if args.no_cache else CachedEncoder(encoder, CACHE_DIR)

    pipeline = TrainingPipeline(
        config,
        ArtifactStore(settings.artifacts_dir, config.model_name),
        encoder_factory=encoder_factory,
        observers=[LoggingObserver(), ReportFileObserver()],
    )
    pipeline.run()


if __name__ == "__main__":
    main()
