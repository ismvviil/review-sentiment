import type { CSSProperties } from 'react'
import { SENTIMENT_META, type Sentiment } from '@/entities/sentiment'
import styles from './model.module.css'

interface Props {
  labels: Sentiment[]
  matrix: number[][]
}

/** Precision, recall and F1 of each class, derived from the confusion matrix. */
export function PerClassTable({ labels, matrix }: Props) {
  const rows = labels.map((label, i) => {
    const tp = matrix[i]?.[i] ?? 0
    const actual = (matrix[i] ?? []).reduce((a, b) => a + b, 0)
    const predicted = matrix.reduce((sum, row) => sum + (row[i] ?? 0), 0)
    const precision = predicted ? tp / predicted : 0
    const recall = actual ? tp / actual : 0
    const f1 = precision + recall ? (2 * precision * recall) / (precision + recall) : 0
    return { label, precision, recall, f1 }
  })
  const hardest = rows.reduce((a, b) => (b.f1 < a.f1 ? b : a))

  return (
    <>
      <div className={styles.perClass}>
        {rows.map((r) => (
          <div key={r.label} className={styles.perClassRow} style={{ '--c': SENTIMENT_META[r.label]?.color } as CSSProperties}>
            <span className={styles.perClassName}>
              <span className={styles.swatch} aria-hidden />
              {SENTIMENT_META[r.label]?.label ?? r.label}
            </span>
            {(['precision', 'recall', 'f1'] as const).map((k) => (
              <span key={k} className={styles.perClassMetric}>
                <span className={styles.perClassKey}>{k === 'f1' ? 'F1' : k}</span>
                <span className={styles.miniTrack}>
                  <span className={styles.miniFill} style={{ width: `${r[k] * 100}%` }} />
                </span>
                <span className={styles.perClassValue}>{r[k].toFixed(2)}</span>
              </span>
            ))}
          </div>
        ))}
      </div>
      <p className={styles.note}>
        <strong>{SENTIMENT_META[hardest.label]?.label}</strong> is the hardest class (F1 {hardest.f1.toFixed(2)}):
        3-star reviews usually mix praise and complaints, so they get confused with both neighbors.
      </p>
    </>
  )
}
