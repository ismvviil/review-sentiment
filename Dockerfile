# Single-container image for online deployment (Render, Koyeb, Railway, Hugging Face...).
# FastAPI serves the REST API *and* the built React app on the same port.
# Embeddings run on ONNX Runtime (no PyTorch): the container needs ~250 MB of RAM.
#   docker build -t review-sentiment . && docker run -p 7860:7860 review-sentiment

# ---------- Stage 1: build the React front end ----------
FROM node:24-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: Python API ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.hf-cache

RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

# 1) Dependencies only (cached layer: rebuilt only when pyproject.toml changes).
#    Same scikit-learn as the one that pickled classifier.joblib (pickles are version-sensitive).
COPY backend/pyproject.toml ./
RUN mkdir -p src/review_sentiment && touch src/review_sentiment/__init__.py \
    && pip install ".[onnx]" "scikit-learn==1.9.1" \
    && pip uninstall -y review-sentiment && rm -rf src build *.egg-info
# 2) The application code (fast layer)
COPY backend/src ./src
RUN pip install --no-deps .

# Bake the ONNX model + tokenizer into the image: the container starts without network access
RUN python -c "from huggingface_hub import hf_hub_download as d; m='sentence-transformers/all-MiniLM-L6-v2'; [d(m, f) for f in ('onnx/model.onnx', 'tokenizer.json', 'sentence_bert_config.json')]"

COPY backend/artifacts ./artifacts
COPY --from=web /web/dist ./static

ENV SENTIMENT_ARTIFACTS_DIR=/app/artifacts \
    SENTIMENT_STATIC_DIR=/app/static \
    SENTIMENT_ENCODER_RUNTIME=onnx \
    SENTIMENT_ENVIRONMENT=prod \
    HF_HUB_OFFLINE=1 \
    PORT=7860

RUN chown -R appuser /app
USER appuser

EXPOSE 7860
CMD ["sh", "-c", "uvicorn review_sentiment.api.app:create_app --factory --host 0.0.0.0 --port ${PORT}"]
