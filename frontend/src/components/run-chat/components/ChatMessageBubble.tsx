import { cn } from "@/lib/utils"

import { Citations } from "./Citations"
import { MessageContent } from "./MessageContent"
import { Notes } from "./Notes"
import { PlotPreview } from "./PlotPreview"
import { TablePreview } from "./TablePreview"
import type { UseRunChatPanelResult } from "../types"

type ChatMessageProps = UseRunChatPanelResult["messages"][number]

function ChatMessageBubble(message: ChatMessageProps) {
  const isUser = message.role === "user"
  const isError = message.status === "error"
  const bubbleClasses = cn(
    "max-w-3xl rounded-lg border p-4 text-sm shadow-xs",
    isUser && !isError && "bg-primary text-primary-foreground",
    !isUser && !isError && "bg-background",
    isError && "border-destructive/40 bg-destructive/10 text-destructive",
  )

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={bubbleClasses}>
        <div className="space-y-3">
          <MessageContent message={message} />
          {message.citations?.length ? <Citations citations={message.citations} /> : null}
          {message.notes?.length ? <Notes notes={message.notes} /> : null}
          {message.tableUrl ? <TablePreview message={message} /> : null}
          {message.plotUrl ? (
            <PlotPreview plotUrl={message.plotUrl} metricKey={message.metricKey} />
          ) : null}
        </div>
      </div>
    </div>
  )
}

export { ChatMessageBubble }
export type { ChatMessageProps }
