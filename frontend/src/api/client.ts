const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api"

type RequestOptions = RequestInit

type RequestInput = {
  endpoint: string
  method?: string
  body?: unknown
  headers?: HeadersInit
  options?: RequestOptions
}

async function requestJSON<T>({
  endpoint,
  method = "GET",
  body,
  headers,
  options,
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

  if (body !== undefined) {
    config.body = JSON.stringify(body)
  }

  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, config)

  if (!response.ok) {
    const detail = await safeReadJSON(response)
    const message = detail?.detail ?? response.statusText
    const error = new Error(message)
    throw error
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

async function safeReadJSON(response: Response) {
  try {
    return await response.json()
  } catch {
    return null
  }
}

export { requestJSON }
