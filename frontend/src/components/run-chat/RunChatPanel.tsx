import { useEffect, useRef, useState } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Spinner } from "@/components/ui/spinner"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

import { ChatMessageBubble } from "./components/ChatMessageBubble"
import { ClearHistoryDialog } from "./components/ClearHistoryDialog"
import { useRunChatPanel } from "./useRunChatPanel"

type RunChatPanelProps = {
  runId: number | null | undefined
  enabled: boolean
  isRunFailed?: boolean
  disabledReason?: string
  runName?: string
}

function RunChatPanel({
  runId,
  enabled,
  isRunFailed = false,
  disabledReason,
  runName,
}: RunChatPanelProps) {
  const {
    messages,
    textareaValue,
    setTextareaValue,
    handleSubmit,
    isSubmitting,
    composerDisabled,
    handleDeleteHistory,
    isDeletingHistory,
  } = useRunChatPanel({ runId, enabled })

  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement | null>(null)
  const endRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (scrollAreaRef.current && endRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]')
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight
      }
    }
  }, [messages])

  const confirmDelete = () => {
    handleDeleteHistory()
    setShowDeleteDialog(false)
  }

  return (
    <>
      <Card
        className={cn(
          "flex flex-col",
          !enabled && "opacity-90",
          isRunFailed && "opacity-50 pointer-events-none",
        )}
      >
        <CardHeader className="flex-shrink-0">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <CardTitle className="text-lg">Run chat</CardTitle>
              <CardDescription>
                Ask questions about {runName ? `run "${runName}"` : "this run"}. Responses may
                include MultiQC-derived tables and plots.
              </CardDescription>
            </div>
            {messages.length > 0 && enabled && !isRunFailed && (
              <Button
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
                disabled={isDeletingHistory || isSubmitting}
              >
                {isDeletingHistory ? (
                  <span className="flex items-center gap-2">
                    <Spinner className="h-3 w-3" />
                    Clearing…
                  </span>
                ) : (
                  "Clear history"
                )}
              </Button>
            )}
          </div>
          {disabledReason ? (
            <p className="text-sm text-muted-foreground">{disabledReason}</p>
          ) : null}
        </CardHeader>

        <CardContent className="flex flex-1 flex-col gap-4 overflow-hidden px-2">
          <ScrollArea ref={scrollAreaRef} className="h-[400px] rounded-md bg-muted/20 px-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessageBubble key={message.id} {...message} />
              ))}
              <div ref={endRef} />
            </div>
          </ScrollArea>

          <form onSubmit={handleSubmit} className="space-y-3">
            <fieldset disabled={composerDisabled} className="space-y-3">
              <Textarea
                value={textareaValue}
                onChange={(event) => setTextareaValue(event.target.value)}
                placeholder={
                  enabled
                    ? "E.g. Which samples look like outliers based on duplication rate?"
                    : "Chat is unavailable until the run completes."
                }
                minLength={1}
                rows={4}
              />
              <div className="flex items-center justify-end gap-2">
                <Button type="submit" disabled={textareaValue.trim().length === 0 || isSubmitting}>
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <Spinner className="h-4 w-4" />
                      Sending…
                    </span>
                  ) : (
                    "Send"
                  )}
                </Button>
              </div>
            </fieldset>
          </form>
        </CardContent>
      </Card>

      <ClearHistoryDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        onConfirm={confirmDelete}
      />
    </>
  )
}

export { RunChatPanel }
