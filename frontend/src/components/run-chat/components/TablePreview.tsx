import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

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
        <div className="rounded-md border bg-background">
          <Table>
            <TableHeader>
              <TableRow>
                {tablePreview.headers.map((header: string) => (
                  <TableHead key={header}>{header}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {tablePreview.rows.map((row: string[], rowIndex: number) => (
                <TableRow key={rowIndex}>
                  {row.map((cell: string, cellIndex: number) => (
                    <TableCell key={cellIndex}>{cell}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
    </div>
  )
}

export { TablePreview }
