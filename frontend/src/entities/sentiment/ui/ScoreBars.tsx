import type { CSSProperties } from 'react'
import { percent, SENTIMENT_META, SENTIMENTS, type Scores, type Sentiment } from '../model'
import styles from './sentiment.module.css'

interface Props {
  scores: Scores
  highlight?: Sentiment
}

/** Probability of each class, always in the same order (negative -> positive). */
export function ScoreBars({ scores, highlight }: Props) {
  return (
    <div className={styles.scores} role="list" aria-label="Probability per sentiment">
      {SENTIMENTS.map((s) => {
        const meta = SENTIMENT_META[s]
        return (
          <div
            key={s}
            role="listitem"
            className={styles.scoreRow}
            data-top={s === highlight}
            style={{ '--c': meta.color } as CSSProperties}
          >
            <span className={styles.scoreLabel}>
              <span className={styles.swatch} aria-hidden />
              {meta.label}
            </span>
            <span className={styles.track}>
              <span className={styles.fill} style={{ width: percent(scores[s], 1) }} />
            </span>
            <span className={styles.scoreValue}>{percent(scores[s])}</span>
          </div>
        )
      })}
    </div>
  )
}
