import { requestJSON } from "./client"

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
    endpoint: "/auth/login/",
    method: "POST",
    body: credentials,
  })
}

async function refreshSession() {
  return await requestJSON<{ detail: string }>({
    endpoint: "/auth/refresh/",
    method: "POST",
    body: {},
  })
}

async function me() {
  return await requestJSON<SessionResponse>({
    endpoint: "/auth/me/",
    method: "GET",
  })
}

async function logout() {
  return await requestJSON<undefined>({
    endpoint: "/auth/logout/",
    method: "POST",
  })
}

export { login, refreshSession, me, logout }
export type { User, LoginRequest, LoginResponse, SessionResponse }
