// Adapter 2: everything runs in the visitor's browser (no server needed).
// Same business rules as the backend's ReviewClassifier (validation, batch limit).
import { ApiError, type ApiResponse } from '@/shared/api/http'
import type { SentimentEngine } from '../engine'
import { SENTIMENTS, type Classification, type ModelCard, type Scores, type Sentiment } from '../model'
import { embed, loadEmbedder } from './embedder'
import { type ExportedClassifier, predictProba } from './linearClassifier'

const MAX_CHARS = 5000
const MAX_BATCH = 100
const MODEL_URL = `${import.meta.env.BASE_URL}model/`

const listeners = new Set<(p: number) => void>()
let lastProgress = 0
const reportProgress = (p: number) => {
  lastProgress = p
  listeners.forEach((l) => l(p))
}

let assets: Promise<{ classifier: ExportedClassifier; card: ModelCard }> | null = null
const loadAssets = () =>
  (assets ??= Promise.all([
    fetch(`${MODEL_URL}classifier.json`).then((r) => r.json() as Promise<ExportedClassifier>),
    fetch(`${MODEL_URL}model_card.json`).then((r) => r.json() as Promise<ModelCard>),
  ]).then(([classifier, card]) => ({ classifier, card })))

function clean(raw: string): string {
  const text = raw.split(/\s+/).filter(Boolean).join(' ')
  if (!text) throw new ApiError(422, 'Invalid review', 'The review is empty.')
  if (text.length > MAX_CHARS)
    throw new ApiError(422, 'Invalid review', `The review is too long (max ${MAX_CHARS} characters).`)
  return text
}

async function classifyMany(reviews: string[], signal?: AbortSignal): Promise<Classification[]> {
  if (reviews.length > MAX_BATCH) throw new ApiError(422, 'Batch too large', `At most ${MAX_BATCH} reviews per batch.`)
  const texts = reviews.map(clean)
  const [{ classifier }, vectors] = await Promise.all([loadAssets(), embed(texts, reportProgress)])
  if (signal?.aborted) throw new DOMException('Aborted', 'AbortError')

  return vectors.map((vector, i) => {
    const probabilities = predictProba(classifier, vector)
    const scores = Object.fromEntries(
      classifier.labels.map((label, k) => [label, Math.round((probabilities[k] ?? 0) * 1e4) / 1e4]),
    ) as Scores
    const sentiment = SENTIMENTS.reduce<Sentiment>((best, s) => (scores[s] > scores[best] ? s : best), 'neutral')
    return { review: reviews[i] ?? '', sentiment, confidence: scores[sentiment], scores }
  })
}

async function timed<T>(work: () => Promise<T>): Promise<ApiResponse<T>> {
  const started = performance.now()
  const data = await work()
  return { data, durationMs: performance.now() - started, requestId: null }
}

export const browserEngine: SentimentEngine = {
  kind: 'browser',
  description: 'Runs entirely in your browser: MiniLM (transformers.js, ONNX) + the exported scikit-learn classifier',

  classify: (review, signal) =>
    timed(async () => (await classifyMany([review], signal))[0] as Classification),

  classifyBatch: (reviews, signal) =>
    timed(async () => {
      const results = await classifyMany(reviews, signal)
      const summary = Object.fromEntries(
        SENTIMENTS.map((s) => [s, results.filter((r) => r.sentiment === s).length]),
      ) as Record<Sentiment, number>
      return { results, summary }
    }),

  modelCard: () => timed(async () => (await loadAssets()).card),

  health: () =>
    timed(async () => {
      try {
        const [{ card }] = await Promise.all([loadAssets(), loadEmbedder(reportProgress)])
        return { status: 'ok' as const, version: 'browser', model_version: card.version, detail: null }
      } catch {
        throw new ApiError(503, 'Model unavailable', 'Could not download the model. Check your connection.')
      }
    }),

  onLoadProgress(listener) {
    listeners.add(listener)
    listener(lastProgress)
    return () => listeners.delete(listener)
  },
}
