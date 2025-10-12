import { Link, useParams } from "react-router-dom"

import { RunStatusBadge } from "@/components/RunStatusBadge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { formatDateTime } from "@/lib/datetime"
import { cn } from "@/lib/utils"
import { useRunDetail } from "@/hooks/useRunDetail"

function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const {
    run,
    isLoading,
    isChatReady,
    isMultiqcAvailable,
    isMultiqcPending,
    handleDownloadMultiqc,
  } = useRunDetail(runId)

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
          <div className="flex flex-col items-end gap-2 sm:flex-row sm:items-center sm:gap-2">
            <Button variant="outline" asChild>
              <Link to="/runs">Back to runs</Link>
            </Button>
            <Button
              disabled={!isMultiqcAvailable || isMultiqcPending}
              variant="brand"
              onClick={handleDownloadMultiqc}
            >
              {isMultiqcPending ? (
                <span className="flex items-center gap-2">
                  <Spinner className="h-4 w-4" />
                  Fetching report…
                </span>
              ) : isMultiqcAvailable ? (
                "Download MultiQC"
              ) : (
                "Download unavailable"
              )}
            </Button>
          </div>
        </div>
      </header>

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
                  <p className="flex items-center gap-2">
                    <span className="font-medium text-foreground">Status:</span>
                    <RunStatusBadge status={run.status} />
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Created:</span>{" "}
                    {formatDateTime(run.created_at)}
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Completed:</span>{" "}
                    {formatDateTime(run.completed_at)}
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
          <Card
            aria-disabled={!isChatReady}
            className={cn(
              "border h-full transition-opacity transition-colors",
              !isChatReady &&
                "pointer-events-none border-muted-foreground/60 bg-muted opacity-60 text-muted-foreground",
            )}
          >
            <CardHeader>
              <CardTitle>Chat activity</CardTitle>
              <CardDescription className={cn(!isChatReady ? "text-muted-foreground" : undefined)}>
                {isChatReady
                  ? "Chat with Claude about this run once endpoints are connected."
                  : "Chat becomes available after the run successfully completes."}
              </CardDescription>
            </CardHeader>
            <CardContent className={cn("space-y-2 text-sm", "text-muted-foreground")}>
              {isLoading ? (
                <div className="flex items-center gap-2 text-foreground">
                  <Spinner />
                  <span>Preparing chat surface…</span>
                </div>
              ) : isChatReady ? (
                <>
                  <p>
                    Embed `ChatPanel` once endpoints are live. Support streaming responses and
                    history via `useRunChat`.
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Future work: add quick prompts, export transcript, and highlight references back
                    to raw data.
                  </p>
                </>
              ) : null}
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  )
}

export default RunDetailPage
