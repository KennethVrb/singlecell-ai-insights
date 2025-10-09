import { useCallback } from "react"
import { Link, Outlet, useNavigate } from "react-router-dom"

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
import logoUrl from "@/assets/logo.svg?url"

function MainLayout() {
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
    <div className="flex min-h-screen w-full flex-col bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b border-slate-900/70 bg-slate-950/95 shadow-[0_8px_24px_rgba(15,23,42,0.6)] backdrop-blur supports-[backdrop-filter]:bg-slate-950/80">
        <div className="relative h-16 w-full overflow-hidden">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_-20%,rgba(56,189,248,0.25),transparent_55%),radial-gradient(circle_at_80%_120%,rgba(168,85,247,0.18),transparent_60%)]" />
            <div className="absolute inset-x-0 bottom-0 h-[2px] bg-gradient-to-r from-transparent via-sky-400/70 to-transparent" />
          </div>
          <div className="relative flex h-full w-full items-center justify-between px-4 md:px-6">
            <div className="flex flex-1 items-center gap-2 text-slate-200">
              <img
                src={logoUrl}
                alt="SingleCell AI Insights"
                className="h-10 w-auto drop-shadow-[0_0_12px_rgba(56,189,248,0.35)]"
              />
              <Link to="/runs" className="text-base font-semibold tracking-wide uppercase">
                SingleCell AI Insights
              </Link>
            </div>
            <div className="flex items-center gap-2 text-slate-200">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2">
                    <Avatar className="size-7">
                      <AvatarFallback className="bg-slate-800 text-slate-100">
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
                    <span className="text-muted-foreground text-xs">
                      {user?.email ?? "unknown"}
                    </span>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>Sign out</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
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
