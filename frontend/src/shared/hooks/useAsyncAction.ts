import { useCallback, useEffect, useRef, useState } from 'react'
import { isAbortError } from '@/shared/api/http'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface State<R> {
  status: Status
  data?: R
  error?: Error
}

/**
 * Runs an async action with:
 *  - cancellation: starting a new run aborts the previous request (no race conditions),
 *  - stale-while-revalidate: the last result stays visible while the next one loads,
 *  - cleanup: pending requests are aborted when the component unmounts.
 */
export function useAsyncAction<A extends unknown[], R>(
  action: (signal: AbortSignal, ...args: A) => Promise<R>,
) {
  const [state, setState] = useState<State<R>>({ status: 'idle' })
  const controllerRef = useRef<AbortController | null>(null)
  const actionRef = useRef(action)

  useEffect(() => {
    actionRef.current = action
  })

  useEffect(() => () => controllerRef.current?.abort(), [])

  const run = useCallback(async (...args: A): Promise<R | undefined> => {
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller
    setState((s) => ({ ...s, status: 'loading', error: undefined }))

    try {
      const data = await actionRef.current(controller.signal, ...args)
      if (!controller.signal.aborted) setState({ status: 'success', data })
      return data
    } catch (error) {
      if (isAbortError(error) || controller.signal.aborted) return undefined
      setState((s) => ({ ...s, status: 'error', error: error as Error }))
      return undefined
    }
  }, [])

  const reset = useCallback(() => {
    controllerRef.current?.abort()
    setState({ status: 'idle' })
  }, [])

  return { ...state, isLoading: state.status === 'loading', run, reset }
}
