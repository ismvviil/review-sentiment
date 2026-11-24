import { type Classification, SENTIMENTS } from '@/entities/sentiment'

const escape = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`

export function toCsv(results: Classification[]): string {
  const header = ['review', 'sentiment', 'confidence', ...SENTIMENTS.map((s) => `p_${s}`)]
  const lines = results.map((r) =>
    [r.review, r.sentiment, r.confidence, ...SENTIMENTS.map((s) => r.scores[s])].map(escape).join(','),
  )
  return [header.join(','), ...lines].join('\n')
}

export function downloadCsv(results: Classification[], filename = 'sentiment-results.csv') {
  const blob = new Blob([`﻿${toCsv(results)}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = Object.assign(document.createElement('a'), { href: url, download: filename })
  link.click()
  URL.revokeObjectURL(url)
}
