// Port: what the UI needs from "something that classifies reviews".
// Two adapters implement it:
//   - api engine     -> calls the FastAPI backend over REST (development, Docker)
//   - browser engine -> runs the same model in the browser (static hosting, e.g. GitHub Pages)
// Features only depend on this interface (Dependency Inversion / Open-Closed).
import type { ApiResponse } from '@/shared/api/http'
import type { BatchClassification, Classification, Health, ModelCard } from './model'

export interface SentimentEngine {
  readonly kind: 'api' | 'browser'
  readonly description: string
  classify(review: string, signal?: AbortSignal): Promise<ApiResponse<Classification>>
  classifyBatch(reviews: string[], signal?: AbortSignal): Promise<ApiResponse<BatchClassification>>
  modelCard(signal?: AbortSignal): Promise<ApiResponse<ModelCard>>
  health(signal?: AbortSignal): Promise<ApiResponse<Health>>
  /** Optional: model download progress (0..1), for engines that load a model locally. */
  onLoadProgress?(listener: (progress: number) => void): () => void
}
