import { type ReactNode, useCallback, useEffect, useMemo, useState } from "react"

import { ApiError, UNAUTHORIZED_EVENT } from "@/api/client"
import {
  logout as logoutRequest,
  login as loginRequest,
  refreshSession as refreshSessionRequest,
  me as sessionRequest,
  type LoginRequest,
  type User,
} from "@/api/auth"

import { AuthContext, type AuthContextValue } from "./auth-context"

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

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

  useEffect(() => {
    let isMounted = true

    async function checkAuthState() {
      try {
        const response = await sessionRequest()
        if (isMounted) {
          setUser(response.user)
        }
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          if (isMounted) {
            setUser(null)
          }
          return
        }
        if (isMounted) {
          setUser(null)
        }
      } finally {
        if (isMounted) {
          setIsBootstrapping(false)
        }
      }
    }

    void checkAuthState()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    if (typeof window === "undefined") {
      return
    }

    const handleUnauthorized = () => {
      setUser(null)
      setIsBootstrapping(false)
    }

    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)

    return () => {
      window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
    }
  }, [])

  const value = useMemo<AuthContextValue>(() => {
    return {
      user,
      isAuthenticated: Boolean(user),
      isBootstrapping,
      login,
      refreshSession,
      logout,
    }
  }, [isBootstrapping, logout, login, refreshSession, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }
