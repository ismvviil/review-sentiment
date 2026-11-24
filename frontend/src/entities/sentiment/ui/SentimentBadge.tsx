import type { CSSProperties } from 'react'
import { SENTIMENT_META, type Sentiment } from '../model'
import styles from './sentiment.module.css'

export function SentimentBadge({ sentiment }: { sentiment: Sentiment }) {
  const meta = SENTIMENT_META[sentiment]
  return (
    <span className={styles.badge} style={{ '--c': meta.color } as CSSProperties}>
      <span className={styles.symbol} aria-hidden>
        {meta.symbol}
      </span>
      {meta.label}
    </span>
  )
}
