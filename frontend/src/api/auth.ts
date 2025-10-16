import { requestJSON } from "./client"
import { API_ENDPOINTS } from "./endpoints"

type LoginRequest = {
  username: string
  password: string
}

type User = {
  username: string
  email: string
}

type LoginResponse = {
  user: User | null
}

type SessionResponse = {
  user: User
}

async function login(credentials: LoginRequest) {
  return await requestJSON<LoginResponse>({
    endpoint: API_ENDPOINTS.AUTH.LOGIN,
    method: "POST",
    body: credentials,
  })
}

async function refreshSession() {
  return await requestJSON<{ detail: string }>({
    endpoint: API_ENDPOINTS.AUTH.REFRESH,
    method: "POST",
    body: {},
  })
}

async function me() {
  return await requestJSON<SessionResponse>({
    endpoint: API_ENDPOINTS.AUTH.ME,
    method: "GET",
  })
}

async function logout() {
  return await requestJSON<undefined>({
    endpoint: API_ENDPOINTS.AUTH.LOGOUT,
    method: "POST",
  })
}

export { login, refreshSession, me, logout }
export type { User, LoginRequest, LoginResponse, SessionResponse }
