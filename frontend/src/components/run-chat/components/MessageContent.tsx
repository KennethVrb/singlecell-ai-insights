import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { ImageLightbox } from "@/components/ui/image-lightbox"
import { Spinner } from "@/components/ui/spinner"

import type { ChatMessageProps } from "./ChatMessageBubble"

function MessageContent({ message, isUser }: { message: ChatMessageProps; isUser: boolean }) {
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

  return <FormattedMessage content={message.content} isUser={message.role === "user"} />
}

function FormattedMessage({ content, isUser }: { content: string; isUser: boolean }) {
  return (
    <div className={`max-w-none [&>*:not(:last-child)]:mb-3 ${isUser ? "[&_*]:!text-white" : ""}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom image renderer to use our lightbox
          img: ({ src, alt }) => {
            if (!src) return null
            return (
              <ImageLightbox
                src={src}
                alt={alt || "Generated plot"}
                className="mx-auto max-w-[70%] cursor-pointer transition-opacity hover:opacity-80"
              />
            )
          },
          // Style lists
          ul: ({ children }) => <ul className="ml-4 list-disc space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="ml-4 list-decimal space-y-1">{children}</ol>,
          // Style paragraphs
          p: ({ children }) => <p>{children}</p>,
          // Style strong/bold
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          // Style code
          code: ({ children, className }) => {
            const isInline = !className
            return isInline ? (
              <code
                className={`rounded px-1 py-0.5 font-mono text-xs ${
                  isUser ? "bg-white/20 !text-white" : "bg-muted text-foreground"
                }`}
              >
                {children}
              </code>
            ) : (
              <code className="block rounded bg-muted p-2 font-mono text-xs">{children}</code>
            )
          },
          // Style headings
          h1: ({ children }) => <h1 className="text-xl font-semibold">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-semibold">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-medium">{children}</h3>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export { MessageContent }
