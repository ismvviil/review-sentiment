"""
Integration layer - REST resource ``/classifications``.

Routes are ``async``. Inference is CPU-bound, so it runs in a worker thread
(``run_in_threadpool``): the event loop stays free to accept other requests meanwhile.
"""

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from review_sentiment.api.dependencies import ClassifierDep
from review_sentiment.api.schemas import (
    BatchClassificationResponse,
    BatchClassifyRequest,
    ClassificationResponse,
    ClassifyRequest,
)

router = APIRouter(prefix="/classifications", tags=["classifications"])


@router.post("", response_model=ClassificationResponse, summary="Classify one review")
async def classify(body: ClassifyRequest, classifier: ClassifierDep) -> ClassificationResponse:
    prediction = await run_in_threadpool(classifier.predict, body.review)
    return ClassificationResponse.from_prediction(body.review, prediction)


@router.post("/batch", response_model=BatchClassificationResponse,
             summary="Classify several reviews in one call")
async def classify_batch(
    body: BatchClassifyRequest, classifier: ClassifierDep
) -> BatchClassificationResponse:
    predictions = await run_in_threadpool(classifier.predict_many, body.reviews)
    return BatchClassificationResponse.build([
        ClassificationResponse.from_prediction(review, p)
        for review, p in zip(body.reviews, predictions, strict=True)
    ])
