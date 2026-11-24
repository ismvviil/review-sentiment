import { useEffect, useState } from 'react'
import { sentimentEngine } from '@/entities/sentiment'
import { useHashRoute } from '@/shared/hooks/useHashRoute'
import { type ThemePreference, useTheme } from '@/shared/hooks/useTheme'
import { type ApiStatus, useApiHealth } from './useApiHealth'
import { VIEW_IDS, VIEWS } from './views'
import styles from './app.module.css'

const THEME_ICON: Record<ThemePreference, string> = { system: '◐', light: '☀', dark: '☾' }

export function App() {
  const route = useHashRoute(VIEW_IDS, 'analyze')
  const view = VIEWS.find((v) => v.id === route) ?? VIEWS[0]
  const { theme, cycle } = useTheme()
  const api = useApiHealth()

  useEffect(() => {
    document.title = `${view.label} · Review Sentiment`
  }, [view])

  const View = view.component

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <a href="#/analyze" className={styles.brand} aria-label="Review Sentiment, home">
            <span className={styles.logo} aria-hidden>
              <span style={{ height: '45%', background: 'var(--sentiment-negative)' }} />
              <span style={{ height: '70%', background: 'var(--sentiment-neutral)' }} />
              <span style={{ height: '100%', background: 'var(--sentiment-positive)' }} />
            </span>
            <span className={styles.brandName}>Review Sentiment</span>
          </a>

          <nav className={styles.nav} aria-label="Main">
            {VIEWS.map((v) => (
              <a
                key={v.id}
                href={`#/${v.id}`}
                className={styles.navLink}
                aria-current={v.id === view.id ? 'page' : undefined}
              >
                {v.label}
              </a>
            ))}
          </nav>

          <span className={styles.spacer} />
          <StatusPill status={api} />
          <button
            type="button"
            className={styles.themeButton}
            onClick={cycle}
            title={`Theme: ${theme} (click to change)`}
            aria-label={`Theme: ${theme}. Change theme`}
          >
            {THEME_ICON[theme]}
          </button>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.intro}>
          <h1 className={styles.title}>{view.title}</h1>
          <p className={styles.lede}>{view.description}</p>
        </div>
        <View key={view.id} />
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <span>{sentimentEngine.description}</span>
          {sentimentEngine.kind === 'api' && (
            <a href="/docs" target="_blank" rel="noreferrer">
              API docs
            </a>
          )}
        </div>
      </footer>
    </div>
  )
}

function StatusPill({ status }: { status: ApiStatus }) {
  const progress = useLoadProgress()
  const inBrowser = sentimentEngine.kind === 'browser'
  const text =
    status.state === 'ready'
      ? `Model ${status.health.model_version ?? ''}${inBrowser ? ' · in your browser' : ''}`
      : status.state === 'unavailable'
        ? inBrowser ? 'Model unavailable' : 'API unavailable'
        : inBrowser ? `Loading model… ${Math.round(progress * 100)}%` : 'Connecting…'
  const title = status.state === 'unavailable' ? status.reason : text

  return (
    <span className={styles.status} data-state={status.state} title={title} role="status">
      <span className={styles.statusDot} aria-hidden />
      <span className={styles.statusText}>{text}</span>
    </span>
  )
}

/** Download progress of a locally executed model (browser engine only). */
function useLoadProgress(): number {
  const [progress, setProgress] = useState(0)
  useEffect(() => sentimentEngine.onLoadProgress?.(setProgress), [])
  return progress
}
