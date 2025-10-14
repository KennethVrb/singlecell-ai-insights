import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"

import type { ChatMessageProps } from "./ChatMessageBubble"

function TablePreview({ message }: { message: ChatMessageProps }) {
  const { tablePreviewStatus, tablePreview, tablePreviewError, tableUrl } = message

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Table preview
        </p>
        {tableUrl ? (
          <Button asChild size="sm" variant="outline">
            <a href={tableUrl} target="_blank" rel="noopener noreferrer">
              Download CSV
            </a>
          </Button>
        ) : null}
      </div>

      {tablePreviewStatus === "loading" ? (
        <p className="flex items-center gap-2 text-muted-foreground">
          <Spinner className="h-4 w-4" />
          Loading preview…
        </p>
      ) : null}

      {tablePreviewStatus === "error" && tablePreviewError ? (
        <p className="text-sm text-destructive">{tablePreviewError}</p>
      ) : null}

      {tablePreviewStatus === "ready" && tablePreview ? (
        <div className="overflow-x-auto rounded-md border bg-background w-[1270px]">
          <table className="w-max min-w-full text-sm">
            <thead className="border-b bg-muted/50">
              <tr>
                {tablePreview.headers.map((header: string) => (
                  <th key={header} className="whitespace-nowrap px-3 py-2 text-left font-medium">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tablePreview.rows.map((row: string[], rowIndex: number) => (
                <tr key={rowIndex} className="border-b last:border-0">
                  {row.map((cell: string, cellIndex: number) => (
                    <td key={cellIndex} className="whitespace-nowrap px-3 py-2">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}

export { TablePreview }
