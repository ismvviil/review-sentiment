import { useCallback, useState } from 'react'

/** useState that survives page reloads (JSON in localStorage). */
export function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key)
      return stored === null ? initial : (JSON.parse(stored) as T)
    } catch {
      return initial
    }
  })

  const update = useCallback(
    (next: T | ((previous: T) => T)) => {
      setValue((previous) => {
        const resolved = next instanceof Function ? next(previous) : next
        try {
          localStorage.setItem(key, JSON.stringify(resolved))
        } catch {
          /* storage full or disabled: keep the in-memory value */
        }
        return resolved
      })
    },
    [key],
  )

  return [value, update] as const
}
