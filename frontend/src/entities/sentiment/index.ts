// Public API of the "sentiment" entity: features import from here, never from inner files.
import { apiEngine } from './api'
import { browserEngine } from './browser/browserEngine'
import type { SentimentEngine } from './engine'

export * from './model'
export type { SentimentEngine } from './engine'
export { SentimentBadge } from './ui/SentimentBadge'
export { ScoreBars } from './ui/ScoreBars'
export { PolaritySpectrum } from './ui/PolaritySpectrum'

/** Chosen at build time: VITE_ENGINE=browser for static hosting, the REST API otherwise. */
export const sentimentEngine: SentimentEngine =
  import.meta.env.VITE_ENGINE === 'browser' ? browserEngine : apiEngine
