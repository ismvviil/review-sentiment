"""
Errors are returned in the standard "Problem Details" format (RFC 9457):

    HTTP/1.1 422
    Content-Type: application/problem+json
    {"type": "about:blank", "title": "Invalid review", "status": 422, "detail": "The review is empty."}

To map a new domain error to an HTTP status, add one entry to ``ERROR_MAP``.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from review_sentiment.domain.errors import (
    BatchTooLargeError,
    DomainError,
    InvalidReviewError,
    ModelNotAvailableError,
)

logger = logging.getLogger(__name__)

ERROR_MAP: dict[type[DomainError], tuple[int, str]] = {
    InvalidReviewError: (status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid review"),
    BatchTooLargeError: (status.HTTP_422_UNPROCESSABLE_CONTENT, "Batch too large"),
    ModelNotAvailableError: (status.HTTP_503_SERVICE_UNAVAILABLE, "Model unavailable"),
}


def problem(status_code: int, title: str, detail: str, **extra) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status_code, "detail": detail, **extra}
    return JSONResponse(body, status_code=status_code, media_type="application/problem+json")


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    code, title = next(
        (v for cls, v in ERROR_MAP.items() if isinstance(exc, cls)),
        (status.HTTP_400_BAD_REQUEST, "Bad request"),
    )
    return problem(code, title, str(exc))


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    detail = "; ".join(f"{e['field']}: {e['message']}" for e in errors) or "Invalid request"
    return problem(status.HTTP_422_UNPROCESSABLE_CONTENT, "Validation error", detail,
                   errors=errors)


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return problem(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error",
                   "An unexpected error occurred.")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
