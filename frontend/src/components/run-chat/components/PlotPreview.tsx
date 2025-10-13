import { Button } from "@/components/ui/button"

function PlotPreview({ plotUrl, metricKey }: { plotUrl: string; metricKey: string | null }) {
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Generated plot
        </p>
        <Button asChild size="sm" variant="outline">
          <a href={plotUrl} target="_blank" rel="noopener noreferrer">
            Download PNG
          </a>
        </Button>
      </div>
      <div className="overflow-hidden rounded-md border bg-background">
        <img
          src={plotUrl}
          alt={metricKey ? `Plot for ${metricKey}` : "Run artifact plot"}
          className="max-h-96 w-full object-contain"
          loading="lazy"
        />
      </div>
    </div>
  )
}

export { PlotPreview }
