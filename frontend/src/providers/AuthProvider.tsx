import { type ReactNode, useMemo, useState } from "react"

import { AuthContext, type AuthContextValue, type AuthUser } from "./auth-context"

type AuthSession = {
  accessToken: string | null
  refreshToken: string | null
}

function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<AuthSession>({
    accessToken: null,
    refreshToken: null,
  })
  const [user, setUser] = useState<AuthUser>(null)

  const value = useMemo<AuthContextValue>(() => {
    return {
      user,
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
      isAuthenticated: Boolean(session.accessToken),
      setSession({ user: nextUser, accessToken, refreshToken }) {
        setUser(nextUser)
        setSessionState({ accessToken, refreshToken })
      },
      clearSession() {
        setUser(null)
        setSessionState({ accessToken: null, refreshToken: null })
      },
    }
  }, [session.accessToken, session.refreshToken, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }
