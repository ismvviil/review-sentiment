import type { CSSProperties } from 'react'
import { percent, SENTIMENT_META, type Sentiment } from '@/entities/sentiment'
import styles from './model.module.css'

interface Props {
  labels: Sentiment[]
  matrix: number[][]
}

/**
 * Rows = true sentiment, columns = predicted. Color intensity = share of the row
 * (sequential scale, one hue), so the diagonal reads as per-class recall.
 */
export function ConfusionMatrix({ labels, matrix }: Props) {
  const name = (s: Sentiment) => SENTIMENT_META[s]?.label ?? s

  return (
    <figure>
      <div className={styles.matrix} style={{ '--n': labels.length } as CSSProperties} role="table" aria-label="Confusion matrix">
        <div role="row" style={{ display: 'contents' }}>
          <span className={styles.axisLabel} role="columnheader">
            True ↓ / Predicted →
          </span>
          {labels.map((l) => (
            <span key={l} role="columnheader" className={`${styles.axisLabel} ${styles.colHead}`}>
              {name(l)}
            </span>
          ))}
        </div>

        {labels.map((trueLabel, i) => {
          const row = matrix[i] ?? []
          const total = row.reduce((a, b) => a + b, 0) || 1
          return (
            <div key={trueLabel} role="row" style={{ display: 'contents' }}>
              <span role="rowheader" className={`${styles.axisLabel} ${styles.rowHead}`}>
                {name(trueLabel)}
              </span>
              {labels.map((predicted, j) => {
                const count = row[j] ?? 0
                const share = count / total
                return (
                  <div
                    key={predicted}
                    role="cell"
                    className={styles.cell}
                    data-diagonal={i === j}
                    data-dark={share > 0.6}
                    style={{ '--intensity': `${Math.round(8 + share * 92)}%` } as CSSProperties}
                    data-tip={`True ${name(trueLabel)} → predicted ${name(predicted)}: ${count} (${percent(share)})`}
                  >
                    <span className={styles.cellValue}>{percent(share)}</span>
                    <span className={styles.cellSub}>{count}</span>
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
      <figcaption className={styles.matrixCaption}>
        <span>Each row sums to 100%. Outlined diagonal = correct predictions (recall).</span>
      </figcaption>
    </figure>
  )
}
