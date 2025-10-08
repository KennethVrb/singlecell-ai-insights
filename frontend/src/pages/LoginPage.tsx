import { Button } from "@/components/ui/button"

function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-10 text-foreground">
      <section className="w-full max-w-md space-y-6 rounded-lg border border-border bg-card p-8 shadow-sm">
        <header className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold">Sign in to continue</h1>
          <p className="text-sm text-muted-foreground">
            This placeholder form will connect to the HealthOmics API once authentication is wired.
          </p>
        </header>

        <form className="space-y-4">
          <div className="space-y-2 text-left">
            <label className="block text-sm font-medium text-foreground" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="scientist@example.com"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40"
            />
          </div>

          <div className="space-y-2 text-left">
            <label className="block text-sm font-medium text-foreground" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40"
            />
          </div>

          <Button className="w-full" type="submit">
            Continue
          </Button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
