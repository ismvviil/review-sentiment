// The trained scikit-learn classifier, exported to JSON by the backend
// (backend/src/review_sentiment/ml/web_export.py). Same formulas as `predict_proba` there.
import type { Sentiment } from '../model'

interface Linear {
  coef: number[][]
  intercept: number[]
}

export type ExportedClassifier =
  | ({ format: 'softmax-linear'; labels: Sentiment[] } & Linear)
  | {
      format: 'calibrated-linear'
      labels: Sentiment[]
      folds: (Linear & { calibrators: { a: number; b: number }[] })[]
    }

const scores = ({ coef, intercept }: Linear, x: Float32Array): number[] =>
  coef.map((row, k) => row.reduce((sum, w, i) => sum + w * (x[i] ?? 0), intercept[k] ?? 0))

const normalize = (p: number[]): number[] => {
  const total = p.reduce((a, b) => a + b, 0)
  return total > 0 ? p.map((v) => v / total) : p.map(() => 1 / p.length)
}

/** One function per exported format: a new format is a new entry (open for extension). */
const FORMULAS: {
  [F in ExportedClassifier['format']]: (m: Extract<ExportedClassifier, { format: F }>, x: Float32Array) => number[]
} = {
  'softmax-linear': (m, x) => {
    const z = scores(m, x)
    const max = Math.max(...z)
    return normalize(z.map((v) => Math.exp(v - max)))
  },
  'calibrated-linear': (m, x) => {
    const perFold = m.folds.map((fold) => {
      const f = scores(fold, x)
      return normalize(f.map((v, k) => {
        const { a, b } = fold.calibrators[k] ?? { a: 0, b: 0 }
        return 1 / (1 + Math.exp(a * v + b))
      }))
    })
    return m.labels.map((_, k) => perFold.reduce((s, p) => s + (p[k] ?? 0), 0) / perFold.length)
  },
}

export function predictProba(model: ExportedClassifier, x: Float32Array): number[] {
  // The cast is safe: FORMULAS is keyed by the same discriminant
  return (FORMULAS[model.format] as (m: ExportedClassifier, x: Float32Array) => number[])(model, x)
}
