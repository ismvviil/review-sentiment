from typing import Annotated

from fastapi import Depends, Request

from review_sentiment.api.container import Container
from review_sentiment.application.review_classifier import ReviewClassifier
from review_sentiment.domain.errors import ModelNotAvailableError


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_classifier(container: Annotated[Container, Depends(get_container)]) -> ReviewClassifier:
    if container.classifier is None:
        raise ModelNotAvailableError(container.startup_error or "The model is not loaded.")
    return container.classifier


ContainerDep = Annotated[Container, Depends(get_container)]
ClassifierDep = Annotated[ReviewClassifier, Depends(get_classifier)]
