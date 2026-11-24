// Thin, typed HTTP client. The only place that knows about fetch, base URLs and the
// backend's error format (RFC 9457 Problem Details).

const BASE_URL: string = import.meta.env.VITE_API_URL ?? ''

export class ApiError extends Error {
  readonly status: number
  readonly title: string
  readonly requestId?: string

  constructor(status: number, title: string, message: string, requestId?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.title = title
    this.requestId = requestId
  }
}

export interface ApiResponse<T> {
  data: T
  durationMs: number
  requestId: string | null
}

interface RequestOptions {
  method?: 'GET' | 'POST'
  json?: unknown
  signal?: AbortSignal
}

interface ProblemDetails {
  title?: string
  detail?: string
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export async function request<T>(
  path: string,
  { method = 'GET', json, signal }: RequestOptions = {},
): Promise<ApiResponse<T>> {
  const started = performance.now()
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      signal,
      headers: {
        Accept: 'application/json',
        ...(json !== undefined && { 'Content-Type': 'application/json' }),
      },
      body: json !== undefined ? JSON.stringify(json) : undefined,
    })
  } catch (error) {
    if (isAbortError(error)) throw error
    throw new ApiError(0, 'Network error', 'Cannot reach the API. Is the backend running?')
  }

  const durationMs = performance.now() - started
  const requestId = response.headers.get('X-Request-ID')
  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    const problem = (body ?? {}) as ProblemDetails
    throw new ApiError(
      response.status,
      problem.title ?? response.statusText,
      problem.detail ?? `Request failed with status ${response.status}`,
      requestId ?? undefined,
    )
  }
  return { data: body as T, durationMs, requestId }
}
