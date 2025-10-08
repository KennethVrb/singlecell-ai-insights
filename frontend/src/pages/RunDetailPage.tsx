import { Link, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"

function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()

  return (
    <main className="flex min-h-screen flex-col gap-6 bg-background px-6 py-10 text-foreground">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">Run details: {runId ?? "unknown"}</h1>
        <p className="text-muted-foreground">
          This page will surface MultiQC metrics, run metadata, and chat UI once the data layer is
          wired.
        </p>
      </header>

      <section className="rounded-lg border border-dashed border-border bg-card p-6 text-sm text-muted-foreground">
        Run-specific content will be loaded here via React Query hooks (`useRun`, `useRunContext`,
        `useRunChat`).
      </section>

      <div className="flex gap-3">
        <Button variant="outline" asChild>
          <Link to="/runs">Back to runs</Link>
        </Button>
        <Button asChild>
          <a href="#download" aria-disabled>
            Download MultiQC (coming soon)
          </a>
        </Button>
      </div>
    </main>
  )
}

export default RunDetailPage
