import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"

function RunsPage() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-8 bg-background px-8 py-16 text-foreground">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-semibold">HealthOmics Runs</h1>
        <p className="text-muted-foreground">
          Replace this placeholder with the run list once the backend endpoints are connected.
        </p>
      </header>

      <div className="flex gap-4">
        <Button variant="secondary" asChild>
          <Link to="/runs/sample-run-id">View example run</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/login">Back to login</Link>
        </Button>
      </div>
    </main>
  )
}

export default RunsPage
