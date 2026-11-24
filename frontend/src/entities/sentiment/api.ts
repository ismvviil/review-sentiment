// Integration layer of the front end: every call to the sentiment REST API lives here.
import { request } from '@/shared/api/http'
import type { BatchClassification, Classification, Health, ModelCard } from './model'

const V1 = '/api/v1'

export const sentimentApi = {
  classify: (review: string, signal?: AbortSignal) =>
    request<Classification>(`${V1}/classifications`, { method: 'POST', json: { review }, signal }),

  classifyBatch: (reviews: string[], signal?: AbortSignal) =>
    request<BatchClassification>(`${V1}/classifications/batch`, {
      method: 'POST',
      json: { reviews },
      signal,
    }),

  modelCard: (signal?: AbortSignal) => request<ModelCard>(`${V1}/model`, { signal }),

  health: (signal?: AbortSignal) => request<Health>('/health/ready', { signal }),
}
