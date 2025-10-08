import { createContext, useContext } from "react"

import type { LoginRequest } from "@/api/auth"

type AuthUser = {
  username: string
  email: string
} | null

type AuthContextValue = {
  user: AuthUser
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  refreshSession: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }

  return context
}

export { AuthContext, useAuth }
export type { AuthContextValue, AuthUser }
