import { useEffect } from 'react'
import { type ModelCard, sentimentEngine } from '@/entities/sentiment'
import { useAsyncAction } from '@/shared/hooks/useAsyncAction'
import { Alert, Button, Card, Skeleton } from '@/shared/ui'
import { ConfusionMatrix } from './ConfusionMatrix'
import { MetricsTable } from './MetricsTable'
import { PerClassTable } from './PerClassTable'
import styles from './model.module.css'

export function ModelView() {
  const { run, data, error, isLoading } = useAsyncAction((signal) => sentimentEngine.modelCard(signal))

  useEffect(() => {
    void run()
  }, [run])

  if (error) {
    return (
      <Alert title="Model information unavailable">
        {error.message}{' '}
        <Button size="sm" variant="ghost" onClick={() => void run()}>
          Retry
        </Button>
      </Alert>
    )
  }

  if (!data) {
    return (
      <Card title="Model card">
        <div style={{ display: 'grid', gap: 12 }} aria-busy={isLoading}>
          <Skeleton width="40%" height={20} />
          <Skeleton height={14} />
          <Skeleton width="70%" height={14} />
        </div>
      </Card>
    )
  }

  const card = data.data
  return (
    <div className={styles.stack}>
      <Card title="Model card" actions={<span className="mono">v{card.version}</span>}>
        <Facts card={card} />
      </Card>
      <Card title="Classifier comparison · train vs test">
        <MetricsTable card={card} />
      </Card>
      <div className={styles.twoCols}>
        <Card title={`Confusion matrix · ${card.classifier} · test set`}>
          <ConfusionMatrix labels={card.labels} matrix={card.confusion_matrix} />
        </Card>
        <Card title="Per-class performance">
          <PerClassTable labels={card.labels} matrix={card.confusion_matrix} />
        </Card>
      </div>
    </div>
  )
}

function Facts({ card }: { card: ModelCard }) {
  const testF1 = card.metrics[card.classifier]?.test.f1
  const facts = [
    { label: 'Served classifier', value: card.classifier, sub: testF1 != null ? `test F1 ${testF1.toFixed(3)}` : undefined },
    {
      label: 'Embedding model',
      value: card.encoder.model_name?.split('/').pop() ?? card.encoder.type,
      sub: card.encoder.dimension ? `${card.encoder.dimension}-dimension vectors` : undefined,
    },
    { label: 'Dataset', value: card.dataset.name ?? '—', sub: card.dataset.label_mapping },
    {
      label: 'Train / test',
      value: `${card.train_size.toLocaleString()} / ${card.test_size.toLocaleString()}`,
      sub: card.dataset.samples_per_class ? `${card.dataset.samples_per_class.toLocaleString()} reviews per class` : undefined,
    },
    { label: 'Trained', value: new Date(card.created_at).toLocaleString(), sub: card.name },
  ]
  return (
    <dl className={styles.facts}>
      {facts.map((f) => (
        <div key={f.label} className={styles.fact}>
          <dt>{f.label}</dt>
          <dd>
            {f.value}
            {f.sub && <span className={styles.factSub}>{f.sub}</span>}
          </dd>
        </div>
      ))}
    </dl>
  )
}
