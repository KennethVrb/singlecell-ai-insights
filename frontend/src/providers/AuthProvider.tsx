import { type ReactNode, useCallback, useMemo, useState } from "react"

import { ApiError } from "@/api/client"
import {
  logout as logoutRequest,
  login as loginRequest,
  refreshSession as refreshSessionRequest,
  type LoginRequest,
} from "@/api/auth"

import { AuthContext, type AuthContextValue, type AuthUser } from "./auth-context"

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser>(null)

  const login = useCallback(async (credentials: LoginRequest) => {
    const response = await loginRequest(credentials)
    if (!response.user) {
      setUser(null)
      throw new Error("Login response did not include a user")
    }

    setUser(response.user)
  }, [])

  const refreshSession = useCallback(async () => {
    try {
      await refreshSessionRequest()
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setUser(null)
        return
      }

      throw error
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutRequest()
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setUser(null)
        return
      }

      setUser(null)
      throw error
    }

    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(() => {
    return {
      user,
      isAuthenticated: Boolean(user),
      login,
      refreshSession,
      logout,
    }
  }, [logout, login, refreshSession, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }
