import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Clock3, TriangleAlert } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { cn } from "@/lib/utils"
import { useAuth } from "@/providers/auth-context"

function RunsPage() {
  const { user } = useAuth()

  const placeholderRuns = [
    {
      id: "sample-run-id",
      name: "SC-2319",
      pipeline: "MultiQC",
      status: "Succeeded",
      samples: 24,
      updatedAt: "2024-08-12",
    },
    {
      id: "sample-run-id-2",
      name: "SC-2320",
      pipeline: "RNA-seq",
      status: "Running",
      samples: 18,
      updatedAt: "2024-08-14",
    },
  ]

  const statusVariants: Record<string, string> = {
    Succeeded: "status-badge status-badge-success",
    Running: "status-badge status-badge-warning",
    Failed: "status-badge status-badge-error",
  }

  const statusIcons: Record<string, ReactNode> = {
    Succeeded: <CheckCircle2 className="size-3.5" aria-hidden />,
    Running: <Clock3 className="size-3.5" aria-hidden />,
    Failed: <TriangleAlert className="size-3.5" aria-hidden />,
  }

  const getStatusBadgeClasses = (status: string) =>
    cn(statusVariants[status] ?? "status-badge status-badge-muted")

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1>HealthOmics runs</h1>
        <p className="text-muted-foreground">
          Review recent sequencing runs, inspect MultiQC metrics, and open detailed views for deeper
          analysis.
        </p>
      </header>

      <section className="rounded-lg border border-dashed border-border bg-card p-4 text-sm text-muted-foreground">
        The table below illustrates the future runs list. Once `useRuns` is wired to `/api/runs/`,
        replace the placeholder data with real records and add sorting or filtering as needed.
      </section>

      <div className="hidden overflow-x-auto rounded-lg border border-border bg-card shadow-sm md:block">
        <Table className="min-w-[720px] text-sm">
          <TableHeader className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
            <TableRow>
              <TableHead className="px-4 py-3">Run</TableHead>
              <TableHead className="px-4 py-3">Pipeline</TableHead>
              <TableHead className="px-4 py-3">Status</TableHead>
              <TableHead className="px-4 py-3">Samples</TableHead>
              <TableHead className="px-4 py-3">Updated</TableHead>
              <TableHead className="px-4 py-3 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {placeholderRuns.map((run) => (
              <TableRow key={run.id}>
                <TableCell className="px-4 py-4 font-medium text-foreground">{run.name}</TableCell>
                <TableCell className="px-4 py-4 text-muted-foreground">{run.pipeline}</TableCell>
                <TableCell className="px-4 py-4">
                  <span className={getStatusBadgeClasses(run.status)}>
                    {statusIcons[run.status]}
                    {run.status}
                  </span>
                </TableCell>
                <TableCell className="px-4 py-4 text-muted-foreground">{run.samples}</TableCell>
                <TableCell className="px-4 py-4 text-muted-foreground">{run.updatedAt}</TableCell>
                <TableCell className="px-4 py-4 text-right">
                  <Button variant="brand" size="sm" asChild>
                    <Link to={`/runs/${run.id}`}>Open</Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="grid gap-4 md:hidden">
        {placeholderRuns.map((run) => (
          <Card key={run.id} className="border border-dashed">
            <CardHeader className="space-y-1">
              <CardTitle className="text-base">{run.name}</CardTitle>
              <CardDescription>{run.pipeline}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center justify-between">
                <span>Status</span>
                <span className={getStatusBadgeClasses(run.status)}>{run.status}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Samples</span>
                <span>{run.samples}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Updated</span>
                <span>{run.updatedAt}</span>
              </div>
              {user ? (
                <p className="text-xs text-muted-foreground/80">Signed in as {user.username}</p>
              ) : null}
              <Button variant="secondary" className="w-full" asChild>
                <Link to={`/runs/${run.id}`}>Open run</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default RunsPage
