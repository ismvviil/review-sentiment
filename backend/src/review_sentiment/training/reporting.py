"""
Observer pattern: the pipeline publishes events; observers decide what to do with them
(print to the console, write a file, send to an experiment tracker...). Adding a new kind of
report means adding an observer, not modifying the pipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from review_sentiment.training.pipeline import TrainingResult

logger = logging.getLogger("review_sentiment.training")


class TrainingObserver(Protocol):
    def on_step(self, message: str) -> None: ...

    def on_classifier_evaluated(self, name: str, metrics: dict[str, dict[str, float]]) -> None: ...

    def on_completed(self, result: TrainingResult) -> None: ...


class LoggingObserver:
    """Progress messages through the standard logger."""

    def on_step(self, message: str) -> None:
        logger.info(message)

    def on_classifier_evaluated(self, name: str, metrics: dict[str, dict[str, float]]) -> None:
        logger.info("%-20s test F1 = %.4f", name, metrics["test"]["f1"])

    def on_completed(self, result: TrainingResult) -> None:
        logger.info("Model saved -> %s", result.artifact_path)


class ReportFileObserver:
    """Writes a human-readable report next to the saved model."""

    def on_step(self, message: str) -> None:
        pass

    def on_classifier_evaluated(self, name: str, metrics: dict[str, dict[str, float]]) -> None:
        pass

    def on_completed(self, result: TrainingResult) -> None:
        report = render_report(result)
        print("\n" + report)
        Path(result.artifact_path, "report.txt").write_text(report, encoding="utf-8")


def render_report(result: TrainingResult) -> str:
    card = result.card
    names = list(card.metrics)
    metric_names = list(next(iter(card.metrics.values()))["test"])
    width = 22 + 7 + 11 * len(metric_names)

    lines = [
        f"Model {card.name} v{card.version}",
        f"Dataset : {card.dataset.get('name')} ({card.train_size} train / {card.test_size} test)",
        f"Encoder : {card.encoder.get('model_name')} ({card.encoder.get('dimension')}-d)",
        "=" * width,
        f"{'Classifier':<22}{'Set':<7}" + "".join(f"{m.capitalize():>11}" for m in metric_names),
        "-" * width,
    ]
    for name in names:
        for split, values in card.metrics[name].items():
            lines.append(f"{name:<22}{split:<7}" + "".join(f"{values[m]:>11.4f}"
                                                         for m in metric_names))
    lines += [
        "=" * width,
        f"Selected: {card.classifier} (best test {card.selection_metric})",
        "",
        result.classification_report,
        f"Confusion matrix (rows = true, columns = predicted) {card.labels}",
        *(f"  {row}" for row in card.confusion_matrix),
    ]
    return "\n".join(lines)
