import { polarity, type Scores } from '../model'
import styles from './sentiment.module.css'

/**
 * Places the review on a negative <-> positive axis.
 * Position = P(positive) - P(negative), mapped from [-1, 1] to [0%, 100%].
 */
export function PolaritySpectrum({ scores }: { scores: Scores }) {
  const value = polarity(scores)
  const left = `${((value + 1) / 2) * 100}%`
  return (
    <div className={styles.spectrum}>
      <div
        className={styles.spectrumTrack}
        role="meter"
        aria-label="Polarity"
        aria-valuemin={-1}
        aria-valuemax={1}
        aria-valuenow={Number(value.toFixed(2))}
        aria-valuetext={`Polarity ${value >= 0 ? '+' : ''}${value.toFixed(2)}`}
      >
        <span className={styles.spectrumMarker} style={{ left }} />
      </div>
      <div className={styles.spectrumAxis} aria-hidden>
        <span>− Negative</span>
        <span>Neutral</span>
        <span>Positive +</span>
      </div>
    </div>
  )
}
