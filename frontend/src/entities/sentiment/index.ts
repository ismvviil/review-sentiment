// Public API of the "sentiment" entity: features import from here, never from inner files.
export * from './model'
export { sentimentApi } from './api'
export { SentimentBadge } from './ui/SentimentBadge'
export { ScoreBars } from './ui/ScoreBars'
export { PolaritySpectrum } from './ui/PolaritySpectrum'
