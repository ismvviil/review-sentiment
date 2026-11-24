import { useEffect, useState } from 'react'
import { type Health, sentimentApi } from '@/entities/sentiment'
import { ApiError, isAbortError } from '@/shared/api/http'

export type ApiStatus =
  | { state: 'checking' }
  | { state: 'ready'; health: Health }
  | { state: 'unavailable'; reason: string }

const POLL_MS = 15_000

/** Polls the readiness probe, and re-checks when the tab regains focus. */
export function useApiHealth(): ApiStatus {
  const [status, setStatus] = useState<ApiStatus>({ state: 'checking' })

  useEffect(() => {
    let controller = new AbortController()

    const check = async () => {
      controller.abort()
      controller = new AbortController()
      try {
        const { data } = await sentimentApi.health(controller.signal)
        setStatus({ state: 'ready', health: data })
      } catch (error) {
        if (isAbortError(error)) return
        setStatus({
          state: 'unavailable',
          reason: error instanceof ApiError ? error.message : 'Unknown error',
        })
      }
    }

    void check()
    const timer = setInterval(check, POLL_MS)
    window.addEventListener('focus', check)
    return () => {
      controller.abort()
      clearInterval(timer)
      window.removeEventListener('focus', check)
    }
  }, [])

  return status
}
