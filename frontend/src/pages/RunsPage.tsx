import { useRunsQuery, useSyncRuns } from "@/api/runs"
import { RunsTable } from "@/components/RunsTable"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
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

      <RunsTable runs={runItems} isLoading={isLoading} currentUserName={user?.username} />
    </div>
  )
}

export default RunsPage
