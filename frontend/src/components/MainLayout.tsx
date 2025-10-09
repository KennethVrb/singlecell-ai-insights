import { useCallback } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"

import { ApiError } from "@/api/client"
import { useAuth } from "@/providers/auth-context"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

function MainLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const isRunDetail = location.pathname.startsWith("/runs/") && location.pathname !== "/runs"

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
    <div className="flex min-h-screen w-full flex-col bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <div className="flex h-16 w-full items-center justify-between px-4 md:px-6">
          <div className="flex flex-1 items-center gap-6">
            <Link to="/runs" className="text-sm font-semibold">
              SingleCell AI Insights
            </Link>
          </div>

          <div className="flex items-center gap-2">
            {isRunDetail ? (
              <Button variant="ghost" size="sm" asChild>
                <Link to="/runs">Back to runs</Link>
              </Button>
            ) : null}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <Avatar className="size-7">
                    <AvatarFallback>
                      {user?.username?.slice(0, 2).toUpperCase() ?? "SC"}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden text-sm font-medium md:inline">
                    {user?.username ?? "Account"}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>
                  Signed in as
                  <br />
                  <span className="text-muted-foreground text-xs">{user?.email ?? "unknown"}</span>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>Sign out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="w-full px-4 py-8 md:px-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export { MainLayout }
