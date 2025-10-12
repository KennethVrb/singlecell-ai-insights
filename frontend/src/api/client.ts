const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api"
const UNAUTHORIZED_EVENT = "auth:unauthorized"
const API_ERROR_EVENT = "api:error"

type ApiErrorEventDetail = {
  status: number
  endpoint: string
  message: string
  detail: unknown
}

class ApiError extends Error {
  status: number
  data: unknown

  constructor(status: number, message: string, data: unknown) {
    super(message)
    this.status = status
    this.data = data
  }
}

type RequestOptions = RequestInit

type RequestInput = {
  endpoint: string
  method?: string
  body?: unknown
  headers?: HeadersInit
  options?: RequestOptions
  params?: Record<string, string>
}

async function requestJSON<T>({
  endpoint,
  method = "GET",
  body,
  headers,
  options,
  params,
}: RequestInput): Promise<T> {
  const config: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    credentials: "include",
    ...options,
  }

  const url = new URL(`${API_BASE_URL}${endpoint}`)

  if (params) {
    Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, value))
  }

  if (body !== undefined) {
    config.body = JSON.stringify(body)
  }

  const response = await fetch(url.toString(), config)

  if (!response.ok) {
    const detail = await safeReadJSON(response)
    const message = getErrorMessage(detail, response.statusText)

    if (typeof window !== "undefined") {
      if (response.status === 401) {
        window.dispatchEvent(
          new CustomEvent(UNAUTHORIZED_EVENT, {
            detail: { status: response.status, endpoint: url.pathname },
          }),
        )
      }
    }

    throw new ApiError(response.status, message, detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

function getErrorMessage(detail: unknown, fallback: string) {
  if (detail && typeof detail === "object" && "detail" in detail) {
    const value = (detail as { detail?: unknown }).detail
    if (typeof value === "string" && value.trim().length > 0) {
      return value
    }
  }

  return fallback
}

async function safeReadJSON(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return null
  }
}

export { requestJSON, ApiError, UNAUTHORIZED_EVENT, API_ERROR_EVENT }
export type { ApiErrorEventDetail }
