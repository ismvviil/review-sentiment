import type { Sentiment } from '@/entities/sentiment'

export interface Example {
  expected: Sentiment | 'mixed'
  text: string
}

export const EXAMPLES: Example[] = [
  { expected: 'positive', text: 'Absolutely love this blender. Powerful, quiet and super easy to clean.' },
  { expected: 'positive', text: 'Arrived a day early and works perfectly. Worth every penny.' },
  { expected: 'neutral', text: 'Decent quality, though the color is a bit different from the photos.' },
  { expected: 'neutral', text: 'It works as described. Packaging was fine, delivery took a week.' },
  { expected: 'negative', text: 'Stopped working after two weeks and customer support never replied.' },
  { expected: 'negative', text: 'Cheap plastic, it broke the first time I used it. Returning it.' },
  { expected: 'mixed', text: 'Not bad at all, but I expected more for this price.' },
]
