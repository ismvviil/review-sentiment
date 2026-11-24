"""Built-in classifiers. Default hyper-parameters can be overridden from the TOML config."""

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from review_sentiment.training.classifiers.base import classifier_registry


@classifier_registry.register("logistic-regression")
def logistic_regression(seed: int, **params) -> LogisticRegression:
    return LogisticRegression(**{"max_iter": 2000, "random_state": seed, **params})


@classifier_registry.register("random-forest")
def random_forest(seed: int, **params) -> RandomForestClassifier:
    return RandomForestClassifier(**{"n_estimators": 300, "n_jobs": -1, "random_state": seed,
                                     **params})


@classifier_registry.register("linear-svm")
def linear_svm(seed: int, **params) -> CalibratedClassifierCV:
    # LinearSVC has no probabilities: calibration adds predict_proba on top of it
    return CalibratedClassifierCV(LinearSVC(**{"random_state": seed, **params}), cv=3)
