import { useCallback, useMemo } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"

import { ApiError } from "@/api/client"
import { useAuth } from "@/providers/auth-context"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarSeparator,
  SidebarTrigger,
} from "@/components/ui/sidebar"
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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

function AppShellLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const navItems = useMemo(
    () => [
      { label: "Runs", href: "/runs", exact: true },
      { label: "Run detail", href: "/runs/:runId", matchPrefix: "/runs/" },
    ],
    [],
  )

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
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background text-foreground">
        <Sidebar>
          <SidebarHeader>
            <Link to="/runs" className="flex items-center gap-2 rounded-md px-2 py-1.5">
              <span className="text-sm font-semibold">SingleCell AI Insights</span>
            </Link>
          </SidebarHeader>

          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Navigation</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => {
                    const isActive = item.exact
                      ? location.pathname === item.href
                      : location.pathname.startsWith(item.matchPrefix ?? item.href)

                    const to = item.href.includes(":")
                      ? item.href.replace(":runId", "sample-run-id")
                      : item.href

                    return (
                      <SidebarMenuItem key={item.href}>
                        <SidebarMenuButton asChild isActive={isActive}>
                          <Link to={to}>{item.label}</Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    )
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter>
            <SidebarSeparator />
            <p className="text-xs text-muted-foreground px-2">HealthOmics MultiQC chatbot POC</p>
          </SidebarFooter>
        </Sidebar>

        <SidebarInset>
          <header className="flex h-16 items-center gap-4 border-b border-border bg-background px-4 md:px-6">
            <SidebarTrigger className="md:hidden" />
            <div className="flex flex-1 items-center justify-between gap-4">
              <div className="flex flex-col">
                <span className="text-sm font-semibold">HealthOmics insights</span>
                <span className="text-xs text-muted-foreground">
                  Inspect run metrics, download reports, and chat with Claude.
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" className="hidden md:inline-flex" asChild>
                  <Link to="/runs">Runs overview</Link>
                </Button>

                <Separator orientation="vertical" className="h-6" />

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
          </header>

          <ScrollArea className="h-[calc(100vh-4rem)]">
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8 md:px-8">
              <Outlet />
            </div>
          </ScrollArea>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}

export { AppShellLayout }
