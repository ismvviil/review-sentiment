import type { MetricSet, ModelCard } from '@/entities/sentiment'
import { cx } from '@/shared/ui/cx'
import styles from './model.module.css'

const TEST_METRICS: (keyof MetricSet)[] = ['accuracy', 'precision', 'recall', 'f1']
const OVERFIT_GAP = 0.1 // train F1 - test F1 above this = the model memorizes the train set

const fmt = (v: number) => v.toFixed(3)
const LABEL: Record<keyof MetricSet, string> = {
  accuracy: 'Accuracy',
  precision: 'Precision',
  recall: 'Recall',
  f1: 'F1',
}

export function MetricsTable({ card }: { card: ModelCard }) {
  const names = Object.keys(card.metrics)
  const best = (metric: keyof MetricSet) =>
    Math.max(...names.map((n) => card.metrics[n]?.test[metric] ?? 0))

  const overfitting = names.filter((n) => gap(card, n) > OVERFIT_GAP)

  return (
    <>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Classifier</th>
              {TEST_METRICS.map((m) => (
                <th key={m} scope="col">
                  Test {LABEL[m]}
                </th>
              ))}
              <th scope="col" className={styles.group}>
                Train F1
              </th>
              <th scope="col">Gap</th>
            </tr>
          </thead>
          <tbody>
            {names.map((name) => {
              const m = card.metrics[name]
              if (!m) return null
              const selected = name === card.classifier
              return (
                <tr key={name} data-selected={selected}>
                  <th scope="row">
                    <span className={styles.name}>
                      {name}
                      {selected && <span className={cx(styles.tag, styles.tagSelected)}>Selected</span>}
                      {overfitting.includes(name) && (
                        <span className={cx(styles.tag, styles.tagWarn)}>Overfitting</span>
                      )}
                    </span>
                  </th>
                  {TEST_METRICS.map((metric) => (
                    <td key={metric} className={cx(m.test[metric] === best(metric) && styles.best)}>
                      {fmt(m.test[metric])}
                    </td>
                  ))}
                  <td className={styles.group}>{fmt(m.train.f1)}</td>
                  <td>{gap(card, name) >= 0 ? '+' : ''}{fmt(gap(card, name))}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className={styles.note}>
        Macro-averaged on {card.test_size.toLocaleString()} test reviews; the classifier with the best test{' '}
        {card.selection_metric.toUpperCase()} is served.{' '}
        {overfitting.length > 0 &&
          `${overfitting.join(', ')} scores much higher on train than on test: it memorizes the training reviews instead of generalizing.`}
      </p>
    </>
  )
}

function gap(card: ModelCard, name: string): number {
  const m = card.metrics[name]
  return m ? m.train.f1 - m.test.f1 : 0
}
