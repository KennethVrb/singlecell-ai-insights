import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { useRunMetricsQuery } from "@/api/runs"

type RunMetricsProps = {
  runId: number | null | undefined
  enabled?: boolean
}

function RunMetrics({ runId, enabled = true }: RunMetricsProps) {
  const { data: metrics, isLoading, error } = useRunMetricsQuery(runId, enabled)

  return (
    <Card className="border">
      <CardHeader>
        <CardTitle>Run metrics</CardTitle>
        <CardDescription>Key quality metrics from MultiQC analysis.</CardDescription>
      </CardHeader>
      <CardContent className="text-sm">
        {isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Spinner />
            <span>Loading metrics…</span>
          </div>
        ) : error ? (
          <p className="text-muted-foreground">
            Metrics not available yet. They will be generated when you first interact with the chat.
          </p>
        ) : metrics ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Total Samples</span>
              <span className="font-semibold text-foreground">{metrics.total_samples}</span>
            </div>

            <div className="space-y-2">
              <div className="max-h-[230px] space-y-2 overflow-y-auto pr-1">
                {metrics.samples.map((sample) => (
                  <div
                    key={sample.name}
                    className="rounded-md border bg-card p-2.5 text-xs transition-colors hover:bg-muted/50"
                  >
                    <div className="mb-1.5 font-medium text-foreground">{sample.name}</div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-muted-foreground">
                      {sample.duplication_rate != null && (
                        <div className="flex justify-between">
                          <span>Duplication:</span>
                          <span className="font-medium text-foreground">
                            {sample.duplication_rate.toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {sample.gc_content != null && (
                        <div className="flex justify-between">
                          <span>GC:</span>
                          <span className="font-medium text-foreground">
                            {sample.gc_content.toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {sample.total_sequences != null && (
                        <div className="col-span-2 flex justify-between">
                          <span>Sequences:</span>
                          <span className="font-medium text-foreground">
                            {(sample.total_sequences / 1_000_000).toFixed(1)}M
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {metrics.samples.length > 3 && (
                <p className="text-xs text-muted-foreground">
                  {metrics.samples.length} samples total
                </p>
              )}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}

export { RunMetrics }
