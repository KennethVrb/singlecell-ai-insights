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

  return <FormattedMessage content={message.content} />
}

function FormattedMessage({ content }: { content: string }) {
  // Parse markdown-style images: ![alt](url)
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g
  const parts: Array<{ type: "text" | "image"; content: string; alt?: string }> = []
  let lastIndex = 0
  let match

  while ((match = imageRegex.exec(content)) !== null) {
    // Add text before the image
    if (match.index > lastIndex) {
      parts.push({ type: "text", content: content.slice(lastIndex, match.index) })
    }
    // Add the image
    parts.push({ type: "image", content: match[2], alt: match[1] })
    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push({ type: "text", content: content.slice(lastIndex) })
  }

  // If no images found, just return the text
  if (parts.length === 0) {
    return <div className="whitespace-pre-wrap leading-relaxed">{content}</div>
  }

  return (
    <div className="space-y-3">
      {parts.map((part, index) => {
        if (part.type === "image") {
          return (
            <img
              key={index}
              src={part.content}
              alt={part.alt || "Generated plot"}
              className="max-w-full"
            />
          )
        }
        return (
          <div key={index} className="whitespace-pre-wrap leading-relaxed">
            {part.content}
          </div>
        )
      })}
    </div>
  )
}

export { MessageContent }
