import { requestJSON } from "./client"

type LoginRequest = {
  username: string
  password: string
}

type LoginResponse = {
  user: {
    username: string
    email: string
  } | null
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

async function logout() {
  return await requestJSON<undefined>({
    endpoint: "/auth/logout/",
    method: "POST",
  })
}

export { login, refreshSession, logout }
export type { LoginRequest, LoginResponse }
