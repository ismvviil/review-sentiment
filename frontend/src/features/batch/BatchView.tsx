import { useState } from 'react'
import { sentimentApi } from '@/entities/sentiment'
import { useAsyncAction } from '@/shared/hooks/useAsyncAction'
import { Alert, Button, Card, EmptyState } from '@/shared/ui'
import { BatchResultsTable } from './BatchResultsTable'
import { DistributionBar } from './DistributionBar'
import styles from './batch.module.css'

const MAX_BATCH = 100

const SAMPLE = [
  'Great sound quality and the battery lasts all week.',
  'The charger stopped working after three days.',
  'It is okay. Does what it says, nothing more.',
  'Super comfortable, I wear them all day without any pain.',
  'Arrived with a scratch on the screen, very disappointed.',
  'Average build quality but fair for the price.',
  'Best purchase I made this year, highly recommend!',
  'Instructions were confusing and two screws were missing.',
  'Works fine, though setup took longer than expected.',
  'Terrible smell when unpacked, had to return it.',
].join('\n')

export function BatchView() {
  const [text, setText] = useState('')
  const reviews = text.split('\n').map((l) => l.trim()).filter(Boolean)
  const tooMany = reviews.length > MAX_BATCH

  const { run, data, error, isLoading } = useAsyncAction((signal, items: string[]) =>
    sentimentApi.classifyBatch(items, signal),
  )

  return (
    <div className={styles.stack}>
      <Card title="Reviews · one per line">
        <label htmlFor="batch" className="visually-hidden">
          Reviews, one per line
        </label>
        <textarea
          id="batch"
          className={styles.textarea}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={'Great product, works perfectly.\nBroke after a week.\nIt is fine for the price.'}
        />
        <div className={styles.toolbar}>
          <span className={styles.counter} data-over={tooMany}>
            {reviews.length} / {MAX_BATCH} reviews
          </span>
          <div className={styles.group}>
            <Button variant="ghost" onClick={() => setText(SAMPLE)}>
              Load sample
            </Button>
            <Button variant="ghost" onClick={() => setText('')} disabled={!text}>
              Clear
            </Button>
            <Button
              variant="primary"
              onClick={() => void run(reviews)}
              disabled={reviews.length === 0 || tooMany}
              loading={isLoading}
            >
              Analyze {reviews.length > 0 ? reviews.length : ''} reviews
            </Button>
          </div>
        </div>
      </Card>

      {error && <Alert title="Batch analysis failed">{error.message}</Alert>}

      {data ? (
        <>
          <Card title="Distribution" actions={<span className="mono">{Math.round(data.durationMs)} ms</span>}>
            <DistributionBar summary={data.data.summary} />
          </Card>
          <Card title="Results">
            <BatchResultsTable results={data.data.results} />
          </Card>
        </>
      ) : (
        !error && (
          <Card>
            <EmptyState title="Analyze many reviews at once">
              Paste up to {MAX_BATCH} reviews, or load the sample to see the sentiment distribution.
            </EmptyState>
          </Card>
        )
      )}
    </div>
  )
}
