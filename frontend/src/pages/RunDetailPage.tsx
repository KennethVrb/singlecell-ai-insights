import { Link, useParams } from "react-router-dom"

import { useRunQuery } from "@/api/runs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const numericRunId = runId ? Number.parseInt(runId, 10) : NaN
  const { data: run, isLoading, isError, error, refetch, isFetching } = useRunQuery(numericRunId)

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1>Run detail</h1>
            <p className="text-muted-foreground">
              Inspect run details, normalized MultiQC metrics, and chat history for run{" "}
              <span className="font-medium text-foreground"> {run?.name ?? "unknown"}</span>.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link to="/runs">Back to runs</Link>
            </Button>
            <Button disabled={!run?.s3_report_key} variant="brand">
              {run?.s3_report_key ? "Download MultiQC" : "Download unavailable"}
            </Button>
          </div>
        </div>
      </header>

      {isError ? (
        <Card className="border border-destructive/40 bg-destructive/5">
          <CardContent className="flex items-center justify-between gap-2 py-6 text-destructive">
            <p>{error instanceof Error ? error.message : "Unable to load run."}</p>
            <Button
              variant="outline"
              onClick={() => refetch({ cancelRefetch: false })}
              disabled={isFetching}
            >
              {isFetching ? <Spinner className="mr-2" /> : null}
              Retry
            </Button>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.35fr)_minmax(0,1fr)]">
        <section className="space-y-6">
          <Card className="border">
            <CardHeader>
              <CardTitle>Run overview</CardTitle>
              <CardDescription>Run details and status.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <Spinner />
                  <span>Loading run…</span>
                </div>
              ) : run ? (
                <div className="space-y-1">
                  <p>
                    <span className="font-medium text-foreground">Name:</span> {run.name}
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Pipeline:</span> {run.pipeline}
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Status:</span>{" "}
                    {run.status || "Unknown"}
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Created:</span>{" "}
                    {run.created_at ? new Date(run.created_at).toLocaleString() : "—"}
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Completed:</span>{" "}
                    {run.completed_at ? new Date(run.completed_at).toLocaleString() : "—"}
                  </p>
                </div>
              ) : (
                <p>Run metadata not available yet. Try refreshing.</p>
              )}
            </CardContent>
          </Card>

          <Card className="border">
            <CardHeader>
              <CardTitle>Run metrics</CardTitle>
              <CardDescription>
                {run?.normalized_context
                  ? "Normalized context ready for visualization."
                  : "Tabs for summary, samples, and quality tables."}
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <Spinner />
                  <span>Loading normalized context…</span>
                </div>
              ) : run?.normalized_context ? (
                <pre className="max-h-64 overflow-auto rounded bg-muted p-3 text-xs">
                  {JSON.stringify(run.normalized_context, null, 2)}
                </pre>
              ) : (
                <p>
                  Normalized context is not yet available. Trigger normalization via the backend or
                  rerun HealthOmics sync.
                </p>
              )}
            </CardContent>
          </Card>
        </section>

        <aside>
          <Card className="border h-full">
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
