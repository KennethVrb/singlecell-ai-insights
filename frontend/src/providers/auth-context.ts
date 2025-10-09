import { createContext, useContext } from "react"

import type { User, LoginRequest } from "@/api/auth"

type AuthContextValue = {
  user: User | null
  isAuthenticated: boolean
  isBootstrapping: boolean
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
export type { AuthContextValue }
