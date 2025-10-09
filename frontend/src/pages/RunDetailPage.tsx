import { Link, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1>Run detail</h1>
            <p className="text-muted-foreground">
              Inspect normalized MultiQC metrics, contextual summaries, and chat history for run
              <span className="font-medium text-foreground"> {runId ?? "unknown"}</span>.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link to="/runs">Back to runs</Link>
            </Button>
            <Button disabled variant="brand">
              Download MultiQC
            </Button>
          </div>
        </div>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.35fr)_minmax(0,1fr)]">
        <section className="space-y-6">
          <Card className="border-dashed">
            <CardHeader>
              <CardTitle>Run overview</CardTitle>
              <CardDescription>Metadata, pipeline, and QC status will render here.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>Hook `useRun` to fetch metrics, timestamps, and AWS provenance.</p>
              <p>Surface summary KPI badges (pass/fail, warnings, total samples).</p>
            </CardContent>
          </Card>

          <Card className="border-dashed">
            <CardHeader>
              <CardTitle>Run metrics</CardTitle>
              <CardDescription>Tabs for summary, samples, and quality tables.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                Integrate `RunMetricsTabs` once the normalization helpers are available. Each tab
                can reuse shadcn tables or charts depending on data.
              </p>
            </CardContent>
          </Card>
        </section>

        <aside>
          <Card className="border-dashed h-full">
            <CardHeader>
              <CardTitle>Chat activity</CardTitle>
              <CardDescription>Claude conversation surface.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                Embed `ChatPanel` once endpoints are live. Support streaming responses and history
                via `useRunChat`.
              </p>
              <p className="text-xs text-muted-foreground">
                Future work: add quick prompts, export transcript, and highlight references back to
                raw data.
              </p>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  )
}

export default RunDetailPage
