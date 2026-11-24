# Production image for the API. Build after training (the model is baked into the image):
#   docker build -t review-sentiment-api ./backend
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf-cache

WORKDIR /app

# CPU-only PyTorch first (much smaller than the CUDA build), then the project
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
COPY pyproject.toml ./
COPY src ./src
RUN pip install .

# Download the embedding model at build time so the container starts offline
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY artifacts ./artifacts
ENV SENTIMENT_ARTIFACTS_DIR=/app/artifacts \
    SENTIMENT_ENVIRONMENT=prod \
    HF_HUB_OFFLINE=1

RUN useradd --create-home appuser && chown -R appuser /app /opt/hf-cache
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready')"

CMD ["uvicorn", "review_sentiment.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
