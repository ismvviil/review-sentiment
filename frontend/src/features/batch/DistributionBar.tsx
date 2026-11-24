import type { CSSProperties } from 'react'
import { percent, SENTIMENT_META, SENTIMENTS, type Sentiment } from '@/entities/sentiment'
import styles from './batch.module.css'

/** Share of each sentiment in the batch: one stacked bar + a legend with counts. */
export function DistributionBar({ summary }: { summary: Record<Sentiment, number> }) {
  const total = SENTIMENTS.reduce((sum, s) => sum + summary[s], 0)
  if (total === 0) return null

  return (
    <figure>
      <div className={styles.distribution} role="img" aria-label={describe(summary, total)}>
        {SENTIMENTS.filter((s) => summary[s] > 0).map((s) => (
          <div
            key={s}
            className={styles.segment}
            style={{ flexGrow: summary[s], '--c': SENTIMENT_META[s].color } as CSSProperties}
            data-tip={`${SENTIMENT_META[s].label}: ${summary[s]} (${percent(summary[s] / total)})`}
          />
        ))}
      </div>
      <figcaption className={styles.legend}>
        {SENTIMENTS.map((s) => (
          <span key={s} className={styles.legendItem} style={{ '--c': SENTIMENT_META[s].color } as CSSProperties}>
            <span className={styles.swatch} aria-hidden />
            {SENTIMENT_META[s].label}
            <strong>{summary[s]}</strong>
            <span>({percent(summary[s] / total)})</span>
          </span>
        ))}
      </figcaption>
    </figure>
  )
}

const describe = (summary: Record<Sentiment, number>, total: number) =>
  SENTIMENTS.map((s) => `${SENTIMENT_META[s].label} ${percent(summary[s] / total)}`).join(', ')
