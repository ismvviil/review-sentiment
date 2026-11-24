import { useEffect, useState } from 'react'

/** Minimal hash router: `#/batch` -> "batch". Deep-linkable, no dependency. */
export function useHashRoute<T extends string>(routes: readonly T[], fallback: T): T {
  const read = (): T => {
    const name = window.location.hash.replace(/^#\/?/, '')
    return (routes as readonly string[]).includes(name) ? (name as T) : fallback
  }
  const [route, setRoute] = useState<T>(read)

  useEffect(() => {
    const onChange = () => setRoute(read())
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return route
}
