import { createContext, useContext } from "react"

type AuthUser = {
  email: string
} | null

type AuthContextValue = {
  user: AuthUser
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setSession: (input: {
    user: AuthUser
    accessToken: string | null
    refreshToken: string | null
  }) => void
  clearSession: () => void
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
