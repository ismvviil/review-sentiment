// Types mirror the backend DTOs (backend/src/review_sentiment/api/schemas.py).

export type Sentiment = 'negative' | 'neutral' | 'positive'

export type Scores = Record<Sentiment, number>

export interface Classification {
  review: string
  sentiment: Sentiment
  confidence: number
  scores: Scores
}

export interface BatchClassification {
  results: Classification[]
  summary: Record<Sentiment, number>
}

export interface MetricSet {
  accuracy: number
  precision: number
  recall: number
  f1: number
}

export interface ModelCard {
  name: string
  version: string
  created_at: string
  classifier: string
  encoder: { type: string; model_name?: string; dimension?: number; [key: string]: unknown }
  dataset: { name?: string; samples_per_class?: number; label_mapping?: string; [key: string]: unknown }
  labels: Sentiment[]
  train_size: number
  test_size: number
  selection_metric: keyof MetricSet
  metrics: Record<string, { train: MetricSet; test: MetricSet }>
  confusion_matrix: number[][]
}

export interface Health {
  status: 'ok' | 'unavailable'
  version: string
  model_version: string | null
  detail: string | null
}

/**
 * Single source of truth for how each sentiment is presented.
 * Open for extension: a new class only needs a new entry here (+ a color token).
 * The symbol is a second, non-color channel so meaning never depends on color alone.
 */
export const SENTIMENTS: readonly Sentiment[] = ['negative', 'neutral', 'positive']

export const SENTIMENT_META: Record<Sentiment, { label: string; symbol: string; color: string }> = {
  negative: { label: 'Negative', symbol: '−', color: 'var(--sentiment-negative)' },
  neutral: { label: 'Neutral', symbol: '=', color: 'var(--sentiment-neutral)' },
  positive: { label: 'Positive', symbol: '+', color: 'var(--sentiment-positive)' },
}

/** Polarity in [-1, 1]: P(positive) - P(negative). 0 means balanced / neutral. */
export const polarity = (scores: Scores): number => scores.positive - scores.negative

export const percent = (value: number, digits = 0): string => `${(value * 100).toFixed(digits)}%`
