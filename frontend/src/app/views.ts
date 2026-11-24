import type { ComponentType } from 'react'
import { AnalyzeView } from '@/features/analyze/AnalyzeView'
import { BatchView } from '@/features/batch/BatchView'
import { ModelView } from '@/features/model/ModelView'

export interface ViewDefinition {
  id: string
  label: string
  title: string
  description: string
  component: ComponentType
}

/** Navigation registry - a new page is one new entry here. */
export const VIEWS = [
  {
    id: 'analyze',
    label: 'Analyze',
    title: 'What does this review feel like?',
    description: 'Paste a product review: the model reads its meaning and tells you if it is positive, neutral or negative.',
    component: AnalyzeView,
  },
  {
    id: 'batch',
    label: 'Batch',
    title: 'Many reviews, one picture',
    description: 'Classify up to 100 reviews in a single request and see how opinions are distributed.',
    component: BatchView,
  },
  {
    id: 'model',
    label: 'Model',
    title: 'Under the hood',
    description: 'How the served model was trained and how well each classifier performed on unseen reviews.',
    component: ModelView,
  },
] as const satisfies readonly ViewDefinition[]

export type ViewId = (typeof VIEWS)[number]['id']
export const VIEW_IDS = VIEWS.map((v) => v.id) as ViewId[]
