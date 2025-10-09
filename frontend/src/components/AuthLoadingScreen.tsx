import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

function AuthLoadingScreen() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-10 text-foreground">
      <Card className="w-full max-w-sm">
        <CardHeader className="space-y-1">
          <CardTitle className="text-xl font-semibold">Restoring your session</CardTitle>
          <CardDescription>Hold tight while we confirm your authentication status.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <Spinner className="size-5" />
            <span className="text-sm text-muted-foreground">Checking credentials…</span>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}

export { AuthLoadingScreen }
