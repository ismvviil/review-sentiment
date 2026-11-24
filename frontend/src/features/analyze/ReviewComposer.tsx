import type { KeyboardEvent } from 'react'
import { Button, Card, Kbd, Switch } from '@/shared/ui'
import { EXAMPLES } from './examples'
import styles from './analyze.module.css'

interface Props {
  value: string
  onChange: (value: string) => void
  onSubmit: (value: string) => void
  onPickExample: (text: string) => void
  live: boolean
  onLiveChange: (live: boolean) => void
  loading: boolean
  maxChars: number
}

export function ReviewComposer({
  value,
  onChange,
  onSubmit,
  onPickExample,
  live,
  onLiveChange,
  loading,
  maxChars,
}: Props) {
  const tooLong = value.length > maxChars
  const canSubmit = value.trim().length > 0 && !tooLong

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && canSubmit) {
      e.preventDefault()
      onSubmit(value)
    }
  }

  return (
    <Card
      title="Review"
      actions={
        <Switch
          checked={live}
          onChange={onLiveChange}
          label="Live analysis"
          title="Classify automatically while you type"
        />
      }
    >
      <label htmlFor="review" className="visually-hidden">
        Product review
      </label>
      <textarea
        id="review"
        className={styles.textarea}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Paste or write a product review… e.g. “The headphones sound great but the battery barely lasts a day.”"
        spellCheck
      />

      <div className={styles.toolbar}>
        <div className={styles.toolbarGroup}>
          <span className={styles.counter} data-over={tooLong}>
            {value.length.toLocaleString()} / {maxChars.toLocaleString()}
          </span>
          {!live && (
            <span className={styles.hint}>
              <Kbd>Ctrl</Kbd> + <Kbd>Enter</Kbd>
            </span>
          )}
        </div>
        <div className={styles.toolbarGroup}>
          <Button variant="ghost" onClick={() => onChange('')} disabled={!value}>
            Clear
          </Button>
          <Button variant="primary" onClick={() => onSubmit(value)} disabled={!canSubmit} loading={loading}>
            Classify
          </Button>
        </div>
      </div>

      <div style={{ marginTop: 'var(--space-5)' }}>
        <p className={styles.label} style={{ marginBottom: 'var(--space-2)' }}>
          Try an example
        </p>
        <div className={styles.examples}>
          {EXAMPLES.map((ex) => (
            <button key={ex.text} type="button" className={styles.chip} onClick={() => onPickExample(ex.text)} title={ex.text}>
              <span className={styles.chipTag}>{ex.expected}</span>
              {ex.text}
            </button>
          ))}
        </div>
      </div>
    </Card>
  )
}
