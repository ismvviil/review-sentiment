// Adapter 1: the FastAPI backend over REST.
import { request } from '@/shared/api/http'
import type { SentimentEngine } from './engine'
import type { BatchClassification, Classification, Health, ModelCard } from './model'

const V1 = '/api/v1'

export const apiEngine: SentimentEngine = {
  kind: 'api',
  description: 'React → REST /api/v1 → FastAPI → ReviewClassifier → MiniLM embeddings + scikit-learn',

  classify: (review, signal) =>
    request<Classification>(`${V1}/classifications`, { method: 'POST', json: { review }, signal }),

  classifyBatch: (reviews, signal) =>
    request<BatchClassification>(`${V1}/classifications/batch`, {
      method: 'POST',
      json: { reviews },
      signal,
    }),

  modelCard: (signal) => request<ModelCard>(`${V1}/model`, { signal }),

  health: (signal) => request<Health>('/health/ready', { signal }),
}
