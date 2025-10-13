import { Spinner } from "@/components/ui/spinner"

import type { ChatMessageProps } from "./ChatMessageBubble"

function MessageContent({ message }: { message: ChatMessageProps }) {
  if (message.status === "pending") {
    return (
      <p className="flex items-center gap-2 text-muted-foreground">
        <Spinner className="h-4 w-4" />
        Thinking…
      </p>
    )
  }

  if (message.status === "error") {
    return <p>{message.error ?? "Something went wrong while contacting the agent."}</p>
  }

  return <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
}

export { MessageContent }
