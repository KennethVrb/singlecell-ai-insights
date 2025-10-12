import { Link } from "react-router-dom"

import { useRunsQuery, useSyncRuns } from "@/api/runs"
import { RunStatusBadge } from "@/components/RunStatusBadge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { formatDateTime } from "@/lib/datetime"
import { useAuth } from "@/providers/auth-context"

function RunsPage() {
  const { user } = useAuth()

  const { data: runs, isLoading, isError, error } = useRunsQuery()
  const { mutate: syncRuns, isPending: isSyncing } = useSyncRuns()

  const runItems = runs ?? []

  return (
    <div className="space-y-8">
      <header className="space-y-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <h1>Sequencing runs</h1>
            <p className="text-muted-foreground">
              Review recent sequencing runs, inspect MultiQC metrics, and open detailed views for
              deeper analysis.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground md:justify-end">
            <Button
              variant="brand"
              size="sm"
              onClick={() => {
                syncRuns()
              }}
              disabled={isSyncing}
            >
              {isSyncing ? <Spinner className="mr-2" /> : null}
              Sync with HealthOmics
            </Button>
          </div>
        </div>
      </header>

      {isError ? (
        <section className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
          {(error instanceof Error ? error.message : "Unable to load runs.") ??
            "Unable to load runs."}
        </section>
      ) : null}

      <div className="hidden overflow-x-auto rounded-lg border border-border bg-card shadow-sm md:block">
        <Table className="min-w-[720px] text-sm">
          <TableHeader className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
            <TableRow>
              <TableHead className="px-4 py-3">Run</TableHead>
              <TableHead className="px-4 py-3">Pipeline</TableHead>
              <TableHead className="px-4 py-3">Status</TableHead>
              <TableHead className="px-4 py-3">Created</TableHead>
              <TableHead className="px-4 py-3">Completed</TableHead>
              <TableHead className="px-4 py-3 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                  <div className="flex items-center justify-center gap-2">
                    <Spinner />
                    <span>Loading runs…</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : runItems.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                  No runs available yet. Try refreshing or check back later.
                </TableCell>
              </TableRow>
            ) : (
              runItems.map((run) => (
                <TableRow key={run.run_id}>
                  <TableCell className="px-4 py-4 font-medium text-foreground">
                    {run.name || run.run_id}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {run.pipeline || "—"}
                  </TableCell>
                  <TableCell className="px-4 py-4">
                    <RunStatusBadge status={run.status} />
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {formatDateTime(run.created_at)}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {formatDateTime(run.completed_at)}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-right">
                    <Button variant="brand" size="sm" asChild>
                      <Link to={`/runs/${run.pk}`}>Open</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="grid gap-4 md:hidden">
        {isLoading ? (
          <Card className="border border-dashed">
            <CardContent className="flex items-center gap-2 text-sm text-muted-foreground">
              <Spinner />
              Loading runs…
            </CardContent>
          </Card>
        ) : runItems.length === 0 ? (
          <Card className="border border-dashed">
            <CardContent className="text-sm text-muted-foreground">
              No runs available yet. Pull to refresh or revisit soon.
            </CardContent>
          </Card>
        ) : (
          runItems.map((run) => (
            <Card key={run.run_id} className="border border-dashed">
              <CardHeader className="space-y-1">
                <CardTitle className="text-base">{run.name || run.run_id}</CardTitle>
                <CardDescription>{run.pipeline || "—"}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <span>Status</span>
                  <RunStatusBadge status={run.status} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Created</span>
                  <span>{formatDateTime(run.created_at)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Completed</span>
                  <span>{formatDateTime(run.completed_at)}</span>
                </div>
                {user ? (
                  <p className="text-xs text-muted-foreground/80">Signed in as {user.username}</p>
                ) : null}
                <Button variant="secondary" className="w-full" asChild>
                  <Link to={`/runs/${run.pk}`}>Open run</Link>
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

export default RunsPage
