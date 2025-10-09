import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/providers/auth-context"

function RunsPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">HealthOmics runs</h1>
        <p className="text-muted-foreground">
          Review recent sequencing runs, inspect MultiQC metrics, and open detailed views for deeper
          analysis.
        </p>
      </header>

      <section className="rounded-lg border border-dashed border-border bg-card p-4 text-sm text-muted-foreground">
        The run list will appear here once React Query hooks are wired to `/api/runs/`. Each entry
        will include status, pipeline, and quick actions for downloads and chat.
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-dashed">
          <CardHeader>
            <CardTitle>Sample run</CardTitle>
            <CardDescription>
              Navigate to a placeholder detail view to explore the layout.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              <p>Additional metadata cards will render in this slot.</p>
              {user ? <p className="mt-2">Signed in as {user.username}</p> : null}
            </div>
            <Button variant="secondary" asChild>
              <Link to="/runs/sample-run-id">Open example</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="border-dashed">
          <CardHeader>
            <CardTitle>Next steps</CardTitle>
            <CardDescription>Coming enhancements for this view.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>• Hook `useRuns` to backend pagination and filters.</p>
            <p>• Surface run health indicators and quick download buttons.</p>
            <p>• Add faceted filtering by pipeline, status, or assay.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default RunsPage
