import { useEffect } from 'react'
import { useLocalStorage } from './useLocalStorage'

export type ThemePreference = 'system' | 'light' | 'dark'

const ORDER: ThemePreference[] = ['system', 'light', 'dark']

export function useTheme() {
  const [theme, setTheme] = useLocalStorage<ThemePreference>('rs.theme', 'system')

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'system') delete root.dataset.theme
    else root.dataset.theme = theme
  }, [theme])

  const cycle = () => setTheme(ORDER[(ORDER.indexOf(theme) + 1) % ORDER.length] ?? 'system')

  return { theme, setTheme, cycle }
}
