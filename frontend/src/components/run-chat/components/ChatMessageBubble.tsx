import { cn } from "@/lib/utils"

import { MessageContent } from "./MessageContent"
import { Notes } from "./Notes"
import type { UseRunChatPanelResult } from "../types"

type ChatMessageProps = UseRunChatPanelResult["messages"][number]

function ChatMessageBubble(message: ChatMessageProps) {
  const isUser = message.role === "user"
  const isError = message.status === "error"
  const bubbleClasses = cn(
    "max-w-full rounded-lg border p-4 text-sm shadow-xs",
    isUser && !isError && "bg-primary text-primary-foreground",
    !isUser && "w-[1300px]",
    !isUser && !isError && "bg-background",
    isError && "border-destructive/40 bg-destructive/10 text-destructive",
  )

  return (
    <div className={cn("flex w-full break-all", isUser ? "justify-end" : "justify-start")}>
      <div className={bubbleClasses}>
        <div>
          <MessageContent message={message} />
          {message.notes?.length ? <Notes notes={message.notes} /> : null}
        </div>
      </div>
    </div>
  )
}

export { ChatMessageBubble }
export type { ChatMessageProps }
