import type { CSSProperties } from 'react'
import { type Classification, percent, SENTIMENT_META } from '@/entities/sentiment'
import { Button, Card } from '@/shared/ui'
import styles from './analyze.module.css'

interface Props {
  items: Classification[]
  onPick: (review: string) => void
  onClear: () => void
}

export function HistoryList({ items, onPick, onClear }: Props) {
  if (items.length === 0) return null
  return (
    <Card
      title="Recent"
      actions={
        <Button variant="ghost" size="sm" onClick={onClear}>
          Clear
        </Button>
      }
    >
      <ul className={styles.history}>
        {items.map((item) => {
          const meta = SENTIMENT_META[item.sentiment]
          return (
            <li key={item.review} className={styles.historyItem}>
              <button
                type="button"
                className={styles.historyButton}
                onClick={() => onPick(item.review)}
                title={`${meta.label}: ${item.review}`}
                style={{ '--c': meta.color } as CSSProperties}
              >
                <span className={styles.historySymbol} aria-label={meta.label}>
                  {meta.symbol}
                </span>
                <span className={styles.historyText}>{item.review}</span>
                <span className={styles.historyConfidence}>{percent(item.confidence)}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </Card>
  )
}
