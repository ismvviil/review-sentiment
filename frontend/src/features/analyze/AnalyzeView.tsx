import { useCallback, useEffect, useState } from 'react'
import { type Classification, sentimentEngine } from '@/entities/sentiment'
import { useAsyncAction } from '@/shared/hooks/useAsyncAction'
import { useDebouncedValue } from '@/shared/hooks/useDebouncedValue'
import { useLocalStorage } from '@/shared/hooks/useLocalStorage'
import { HistoryList } from './HistoryList'
import { PredictionPanel } from './PredictionPanel'
import { ReviewComposer } from './ReviewComposer'
import styles from './analyze.module.css'

const MAX_CHARS = 5000
const HISTORY_SIZE = 8
const LIVE_DELAY_MS = 600
const LIVE_MIN_CHARS = 12

export function AnalyzeView() {
  const [text, setText] = useState('')
  const [live, setLive] = useLocalStorage('rs.live', false)
  const [history, setHistory] = useLocalStorage<Classification[]>('rs.history', [])

  const { run, data, error, isLoading } = useAsyncAction((signal, review: string) =>
    sentimentEngine.classify(review, signal),
  )

  const classify = useCallback(
    async (review: string, { remember = true } = {}) => {
      const trimmed = review.trim()
      if (!trimmed || trimmed.length > MAX_CHARS) return
      const response = await run(trimmed)
      if (response && remember) {
        setHistory((h) =>
          [response.data, ...h.filter((x) => x.review !== response.data.review)].slice(0, HISTORY_SIZE),
        )
      }
    },
    [run, setHistory],
  )

  // Live mode: classify once the user pauses typing. Older requests are aborted automatically.
  const debouncedText = useDebouncedValue(text, LIVE_DELAY_MS)
  useEffect(() => {
    if (live && debouncedText.trim().length >= LIVE_MIN_CHARS) {
      void classify(debouncedText, { remember: false })
    }
  }, [live, debouncedText, classify])

  const pick = (review: string) => {
    setText(review)
    void classify(review)
  }

  return (
    <div className={styles.layout}>
      <div className={styles.column}>
        <ReviewComposer
          value={text}
          onChange={setText}
          onSubmit={(value) => void classify(value)}
          onPickExample={pick}
          live={live}
          onLiveChange={setLive}
          loading={isLoading}
          maxChars={MAX_CHARS}
        />
      </div>
      <div className={styles.column}>
        <PredictionPanel result={data} error={error} loading={isLoading} />
        <HistoryList items={history} onPick={pick} onClear={() => setHistory([])} />
      </div>
    </div>
  )
}
