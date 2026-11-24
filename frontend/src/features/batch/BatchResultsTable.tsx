import { type CSSProperties, useMemo, useState } from 'react'
import {
  type Classification,
  percent,
  SENTIMENT_META,
  SentimentBadge,
  SENTIMENTS,
  type Sentiment,
} from '@/entities/sentiment'
import { Button } from '@/shared/ui'
import { downloadCsv } from './csv'
import styles from './batch.module.css'

type Filter = Sentiment | 'all'

export function BatchResultsTable({ results }: { results: Classification[] }) {
  const [filter, setFilter] = useState<Filter>('all')

  const rows = useMemo(
    () =>
      results
        .map((r, i) => ({ ...r, index: i + 1 }))
        .filter((r) => filter === 'all' || r.sentiment === filter),
    [results, filter],
  )

  const count = (s: Sentiment) => results.filter((r) => r.sentiment === s).length

  return (
    <div className={styles.stack}>
      <div className={styles.toolbar} style={{ marginTop: 0 }}>
        <div className={styles.filters} role="group" aria-label="Filter by sentiment">
          <button type="button" className={styles.filter} aria-pressed={filter === 'all'} onClick={() => setFilter('all')}>
            All · {results.length}
          </button>
          {SENTIMENTS.map((s) => (
            <button key={s} type="button" className={styles.filter} aria-pressed={filter === s} onClick={() => setFilter(s)}>
              {SENTIMENT_META[s].label} · {count(s)}
            </button>
          ))}
        </div>
        <Button size="sm" onClick={() => downloadCsv(results)}>
          Export CSV
        </Button>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>#</th>
              <th>Review</th>
              <th>Sentiment</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.index}>
                <td className={styles.index}>{r.index}</td>
                <td className={styles.reviewCell}>{r.review}</td>
                <td>
                  <SentimentBadge sentiment={r.sentiment} />
                </td>
                <td className={styles.confidenceCell}>
                  <div className={styles.miniBar} style={{ '--c': SENTIMENT_META[r.sentiment].color } as CSSProperties}>
                    <span className={styles.miniTrack}>
                      <span className={styles.miniFill} style={{ width: percent(r.confidence, 1) }} />
                    </span>
                    {percent(r.confidence)}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
