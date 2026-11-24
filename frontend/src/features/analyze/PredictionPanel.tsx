import type { CSSProperties } from 'react'
import {
  type Classification,
  PolaritySpectrum,
  percent,
  ScoreBars,
  SENTIMENT_META,
} from '@/entities/sentiment'
import type { ApiResponse } from '@/shared/api/http'
import { Alert, Card, EmptyState, Skeleton } from '@/shared/ui'
import styles from './analyze.module.css'

interface Props {
  result?: ApiResponse<Classification>
  error?: Error
  loading: boolean
}

export function PredictionPanel({ result, error, loading }: Props) {
  return (
    <Card
      title="Prediction"
      actions={
        loading && result ? (
          <span className={styles.updating} aria-live="polite">
            Updating…
          </span>
        ) : null
      }
    >
      <div aria-live="polite" aria-busy={loading}>
        {error ? (
          <Alert title="Could not classify the review">{error.message}</Alert>
        ) : result ? (
          <Result result={result} stale={loading} />
        ) : loading ? (
          <div className={styles.skeletonStack}>
            <Skeleton width="55%" height={40} />
            <Skeleton height={10} />
            <Skeleton height={60} />
          </div>
        ) : (
          <EmptyState title="No review analyzed yet">
            Write a review or pick an example to see its sentiment.
          </EmptyState>
        )}
      </div>
    </Card>
  )
}

function Result({ result, stale }: { result: ApiResponse<Classification>; stale: boolean }) {
  const { data, durationMs, requestId } = result
  const meta = SENTIMENT_META[data.sentiment]

  return (
    <div className={styles.prediction} data-stale={stale} style={{ '--c': meta.color } as CSSProperties}>
      <div className={styles.verdictRow}>
        <div className={styles.verdict}>
          <span className={styles.verdictSymbol} aria-hidden>
            {meta.symbol}
          </span>
          {meta.label}
        </div>
        <div className={styles.confidence}>
          <div className={styles.confidenceValue}>{percent(data.confidence)}</div>
          <div className={styles.label}>confidence</div>
        </div>
      </div>

      <PolaritySpectrum scores={data.scores} />
      <ScoreBars scores={data.scores} highlight={data.sentiment} />

      <div className={styles.meta}>
        <span>Answered in {Math.round(durationMs)} ms</span>
        {requestId && (
          <span>
            Request <code>{requestId}</code>
          </span>
        )}
      </div>
    </div>
  )
}
