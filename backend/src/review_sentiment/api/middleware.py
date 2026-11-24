"""Cross-cutting HTTP concerns: request id, timing and access log for every request."""

import logging
import time
import uuid

from fastapi import FastAPI, Request

logger = logging.getLogger("review_sentiment.access")


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.1f}"
        logger.info("%s %s -> %d in %.1f ms [%s]", request.method, request.url.path,
                    response.status_code, elapsed_ms, request_id)
        return response
