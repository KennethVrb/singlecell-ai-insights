import { useCallback } from "react"
import { Link, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { ApiError } from "@/api/client"
import { useAuth } from "@/providers/auth-context"

function RunsPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = useCallback(async () => {
    try {
      await logout()
    } catch (error) {
      if (error instanceof ApiError && error.status !== 401) {
        console.error("Logout failed", error)
      }
    } finally {
      navigate("/login", { replace: true })
    }
  }, [logout, navigate])

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 bg-background px-8 py-16 text-foreground">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-semibold">HealthOmics Runs</h1>
        <p className="text-muted-foreground">
          Replace this placeholder with the run list once the backend endpoints are connected.
        </p>
      </header>

      <div className="flex flex-col items-center gap-2 text-sm text-muted-foreground">
        {user ? <p>Signed in as {user.username}</p> : <p>You are not signed in.</p>}
      </div>

      <div className="flex gap-4">
        <Button variant="secondary" asChild>
          <Link to="/runs/sample-run-id">View example run</Link>
        </Button>
        <Button variant="outline" onClick={handleLogout}>
          Sign out
        </Button>
      </div>
    </main>
  )
}

export default RunsPage
