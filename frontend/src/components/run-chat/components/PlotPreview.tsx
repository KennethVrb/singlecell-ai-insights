import { Button } from "@/components/ui/button"
import { ImageLightbox } from "@/components/ui/image-lightbox"

function PlotPreview({ plotUrl, metricKey }: { plotUrl: string; metricKey: string | null }) {
  return (
    <div className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Plot Preview
        </p>
        <Button asChild size="sm" variant="outline">
          <a href={plotUrl} target="_blank" rel="noopener noreferrer">
            Download PNG
          </a>
        </Button>
      </div>
      <div className="max-w-full overflow-hidden">
        <ImageLightbox
          src={plotUrl}
          alt={metricKey ? `Plot for ${metricKey}` : "Run artifact plot"}
          className="max-h-80 max-w-full cursor-pointer object-contain transition-opacity hover:opacity-80"
        />
      </div>
    </div>
  )
}

export { PlotPreview }
