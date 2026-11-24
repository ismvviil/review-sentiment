# Review Sentiment — Homework 2

Classify product reviews as **positive**, **neutral** or **negative** with sentence embeddings + classical ML,
served by a layered **FastAPI** backend and a **React + TypeScript** front end.

```
"Stopped working after two weeks."  ──►  React  ──►  POST /api/v1/classifications  ──►  negative (99%)
```

| | |
|---|---|
| Dataset | [`mteb/amazon_reviews_multi`](https://huggingface.co/datasets/mteb/amazon_reviews_multi) (en), 200k Amazon reviews · 1-2★ negative, 3★ neutral, 4-5★ positive · balanced subset 6,000 / class |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` → 384-d vectors |
| Classifiers | Logistic Regression · Random Forest · Linear SVM (calibrated) — best test F1 is served |
| Backend | Python 3.12+, FastAPI, Pydantic v2, scikit-learn — clean / hexagonal architecture, 34 tests |
| Front end | React 19, TypeScript, Vite, CSS Modules — feature-sliced structure, light & dark themes |

---

## Results (test set, 3,600 reviews)

| Classifier | Accuracy | Precision | Recall | F1 | Train F1 | Gap |
|---|---|---|---|---|---|---|
| logistic-regression | 0.673 | 0.669 | 0.673 | 0.670 | 0.684 | +0.014 |
| random-forest | 0.632 | 0.626 | 0.632 | 0.627 | **1.000** | **+0.373** ⚠ overfitting |
| **linear-svm** (served) | **0.678** | **0.672** | **0.678** | **0.672** | 0.685 | +0.013 |

Neutral is the hardest class (F1 0.54): 3-star reviews mix praise and complaints.
Full report: `backend/artifacts/sentiment-classifier/<version>/report.txt` · also visible on the **Model** page.

---

## Repository layout

```
Projet 2/
├── backend/                          Python project (one package, two entry points)
│   ├── pyproject.toml                dependencies, pytest & ruff config, `sentiment-train` script
│   ├── configs/training.toml         the experiment: dataset, encoder, classifiers, metric
│   ├── src/review_sentiment/
│   │   ├── domain/                   pure business objects — no framework, no ML library
│   │   │   ├── sentiment.py          Sentiment enum · Review (value object) · Prediction
│   │   │   ├── model_card.py         description + metrics of a trained model
│   │   │   ├── ports.py              SentimentPredictor interface (what the app needs)
│   │   │   └── errors.py             domain errors
│   │   ├── application/
│   │   │   └── review_classifier.py  ReviewClassifier.classify(review: str) -> Sentiment
│   │   ├── ml/                       infrastructure shared by training AND serving
│   │   │   ├── encoders/             TextEncoder plugins (sentence-transformer, …)
│   │   │   ├── predictor.py          adapter: embeddings + classifier → SentimentPredictor
│   │   │   └── artifacts.py          versioned model storage (repository)
│   │   ├── training/                 Stage 1 — offline pipeline
│   │   │   ├── datasets/             dataset plugins (amazon-reviews-multi, …)
│   │   │   ├── classifiers/          classifier plugins (logistic-regression, …)
│   │   │   ├── metrics.py            metric registry (accuracy, precision, recall, f1)
│   │   │   ├── embedding_cache.py    caching decorator around any encoder
│   │   │   ├── reporting.py          observers (log, report file)
│   │   │   ├── pipeline.py           the training steps
│   │   │   └── cli.py                `python -m review_sentiment.training`
│   │   ├── api/                      Stage 2 — REST integration layer
│   │   │   ├── app.py                application factory, lifespan, routers
│   │   │   ├── container.py          composition root (wires concrete classes)
│   │   │   ├── dependencies.py       dependency injection for routes
│   │   │   ├── routers/              health · classifications · model
│   │   │   ├── schemas.py            DTOs (request / response contract)
│   │   │   ├── errors.py             domain errors → RFC 9457 problem+json
│   │   │   └── middleware.py         request id, timing, access log
│   │   └── core/                     config (env vars) · logging · plugin registry
│   ├── tests/                        unit + API tests (fake model injected) + real-model test
│   ├── artifacts/                    trained models (generated)  sentiment-classifier/<version>/
│   ├── data/raw/                     dataset file (downloaded)
│   ├── postman/                      Postman collection
│   └── Dockerfile
├── frontend/                         React + TypeScript
│   ├── src/
│   │   ├── app/                      shell: header, navigation registry, API status, theme
│   │   ├── features/                 one folder per page
│   │   │   ├── analyze/              single review, live mode, history, examples
│   │   │   ├── batch/                many reviews, distribution chart, table, CSV export
│   │   │   └── model/                model card, classifier comparison, confusion matrix
│   │   ├── entities/sentiment/       types, API client, presentation metadata, shared visuals
│   │   └── shared/                   generic: http client, hooks, UI primitives, design tokens
│   ├── nginx.conf · Dockerfile
│   └── vite.config.ts · tsconfig.json
└── docker-compose.yml                production-like stack (web + api)
```

---

## Architecture

```
                         ┌──────────────── frontend (React) ────────────────┐
                         │ features → entities/sentiment/api → shared/http  │
                         └───────────────────────┬──────────────────────────┘
                                   JSON over HTTP │  async fetch + AbortController
┌────────────────────────────────────────────────▼──────────────────────────────────────┐
│ api/            routers · schemas (DTO) · errors · middleware        INTEGRATION LAYER │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ application/    ReviewClassifier  (business rules: validation, batch limit)  USE CASE │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ domain/         Sentiment · Review · Prediction · ModelCard · SentimentPredictor port │
└───────────────────────────────────────────────▲───────────────────────────────────────┘
                                                │ implements the port
┌───────────────────────────────────────────────┴───────────────────────────────────────┐
│ ml/             EmbeddingSentimentPredictor · TextEncoder plugins · ArtifactStore     │
└───────────────────────────────────────────────▲───────────────────────────────────────┘
                                                │ writes versioned artifacts
                               training/  dataset → split → encode → classifiers → metrics
```

Dependencies point **inwards**: `domain` imports nothing from the other layers, `application` only knows
the domain, and the ML libraries are hidden behind the `SentimentPredictor` port.

### Design patterns

| Pattern | Where |
|---|---|
| Layered / Hexagonal (ports & adapters) | `domain` ← `application` ← `api`; `ml` implements `domain/ports.py` |
| Dependency Injection + Composition Root | `api/container.py`, `api/dependencies.py`, `create_app(classifier_factory=…)` |
| Registry + Plugin discovery | `core/registry.py` — datasets, encoders, classifiers, metrics |
| Factory | `build_encoder`, `build_classifier`, `build_dataset`, `create_app` |
| Strategy | interchangeable encoders / classifiers chosen by config |
| Decorator | `CachedEncoder` wraps any encoder |
| Observer | training events → `LoggingObserver`, `ReportFileObserver` |
| Repository | `ArtifactStore` (versioned models + `LATEST` pointer) |
| Template Method | fixed steps in `TrainingPipeline.run()` |
| Value Object / DTO | `Review`, `Prediction` · Pydantic schemas |
| Singleton | settings (`lru_cache`), model loaded once at startup |

### Open for extension, closed for modification

| To add… | Do this (no existing code changes) |
|---|---|
| a classifier | new file in `training/classifiers/` with `@classifier_registry.register("knn")`, then list it in `configs/training.toml` |
| a dataset | new file in `training/datasets/` with `@dataset_registry.register("imdb")`, set `[dataset] type` |
| an embedding model | change `model_name` in the config — or a new file in `ml/encoders/` for another library |
| a metric | `metric_registry.register("kappa")(cohen_kappa_score)` |
| a training report | a new observer passed to `TrainingPipeline` |
| an error → HTTP status | one entry in `ERROR_MAP` (`api/errors.py`) |
| a front-end page | a folder in `features/` + one entry in `app/views.ts` |
| a sentiment class | one entry in `SENTIMENT_META` + a color token |

Training and serving share the same encoder code and the encoder spec is saved in the model card,
so the API always rebuilds exactly the encoder the model was trained with.

### REST API (`/docs` for Swagger)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/live` | process is up |
| GET | `/health/ready` | model loaded (503 otherwise) |
| POST | `/api/v1/classifications` | `{"review": "…"}` → sentiment, confidence, scores |
| POST | `/api/v1/classifications/batch` | `{"reviews": [...]}` → results + summary (max 100) |
| GET | `/api/v1/model` | model card: classifier, encoder, dataset, metrics, confusion matrix |

Errors use **RFC 9457 Problem Details** (`application/problem+json`). Every response carries
`X-Request-ID` and `Server-Timing` headers. Inference runs in a worker thread (`run_in_threadpool`) so async
routes never block the event loop.

---

## Run it

```bash
# Python environment (from the project root)
python -m venv .venv
.venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e "backend[train,dev]"

# Dataset (53 MB)
curl -L -o backend/data/raw/amazon_reviews_en_train.jsonl ^
  https://huggingface.co/datasets/mteb/amazon_reviews_multi/resolve/main/en/train.jsonl

# Stage 1 - train (≈8 min the first time, ≈2 min afterwards thanks to the embedding cache)
cd backend
python -m review_sentiment.training

# Tests
pytest

# Stage 2 - API  ->  http://127.0.0.1:8000/docs
uvicorn review_sentiment.api.app:create_app --factory --reload

# Front end (another terminal)  ->  http://localhost:5173
cd frontend
npm install
npm run dev
```

Production-like (after training): `docker compose up --build` → http://localhost:8080

---

## Deploy online (free)

The root `Dockerfile` builds **one container**: FastAPI serves the API *and* the React build on the same URL.
Embeddings run on **ONNX Runtime** instead of PyTorch (`SENTIMENT_ENCODER_RUNTIME=onnx`): same vectors
(verified: cosine 1.000000, identical predictions on 300 test reviews) with ~250 MB of RAM instead of ~800 MB,
so it fits free 512 MB instances. Tested locally under a 512 MB limit: idle 235 MB, peak 312 MB with
3 × 100-review batches.

**Render** (free plan, uses `render.yaml`):
1. Push this repository to GitHub.
2. render.com → **New → Blueprint** → select the repository → **Apply**.
3. The first build takes ~5-10 min; the app is then at `https://review-sentiment-xxxx.onrender.com`.

Free instances sleep after 15 min without traffic; the next visit wakes them up in ~1 min.
Every `git push` redeploys automatically. Any Docker host works the same way (it reads `$PORT`).

Postman: import `backend/postman/ReviewClassifier.postman_collection.json`.

> **Windows:** if `import torch` fails with `WinError 126 … shm.dll`, the Visual C++ runtime is too old.
> Install the latest [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe), or without admin
> rights: `pip install msvc-runtime` and copy `.venv\*.dll` into `.venv\Lib\site-packages\torch\lib\`.
