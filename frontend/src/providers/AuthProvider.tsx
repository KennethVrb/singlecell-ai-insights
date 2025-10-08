import { type ReactNode, useMemo, useState } from "react"

import { AuthContext, type AuthContextValue, type AuthUser } from "./auth-context"

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser>(null)

  const value = useMemo<AuthContextValue>(() => {
    return {
      user,
      isAuthenticated: Boolean(user),
      setSession({ user: nextUser }) {
        setUser(nextUser)
      },
      clearSession() {
        setUser(null)
      },
    }
  }, [user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }
