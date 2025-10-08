import { requestJSON } from "./client"

type LoginRequest = {
  email: string
  password: string
}

type LoginResponse = {
  access: string
  refresh: string
  user: {
    email: string
  }
}

async function login(credentials: LoginRequest) {
  return await requestJSON<LoginResponse>({
    endpoint: "/auth/login/",
    method: "POST",
    body: credentials,
    options: { skipAuth: true },
  })
}

async function refreshToken(refresh: string) {
  return await requestJSON<{ access: string; refresh: string }>({
    endpoint: "/auth/refresh/",
    method: "POST",
    body: { refresh },
    options: { skipAuth: true },
  })
}

export { login, refreshToken }
export type { LoginRequest, LoginResponse }
