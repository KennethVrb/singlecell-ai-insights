import { Download } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { Button } from "@/components/ui/button"
import { ImageLightbox } from "@/components/ui/image-lightbox"
import { Spinner } from "@/components/ui/spinner"

import type { ChatMessageProps } from "./ChatMessageBubble"

function ScrollableTable({ children }: { children: React.ReactNode }) {
  return (
    <div className="my-4">
      <div className="overflow-x-auto rounded-md border w-[1270px]">
        <table className="w-full text-sm">{children}</table>
      </div>
    </div>
  )
}

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
                className="mx-auto max-w-[90%] cursor-pointer transition-opacity hover:opacity-80"
              />
            )
          },
          // Custom link renderer - style download links as buttons
          a: ({ href, children }) => {
            if (!href) return <span>{children}</span>

            const isDownloadLink =
              href.includes("multiqc") ||
              href.includes(".csv") ||
              href.includes(".txt") ||
              href.includes(".png") ||
              String(children).toLowerCase().includes("download")

            if (isDownloadLink) {
              // Extract clean button text - if children is the URL, use a default label
              let buttonText = children
              if (typeof children === "string" && children.startsWith("http")) {
                buttonText = "Download File"
              }

              return (
                <Button asChild size="sm" variant="outline" className="my-2">
                  <a href={href} target="_blank" rel="noopener noreferrer">
                    <Download className="mr-2 h-4 w-4" />
                    {buttonText}
                  </a>
                </Button>
              )
            }

            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className={`underline hover:no-underline ${isUser ? "text-white" : "text-primary"}`}
              >
                {children}
              </a>
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
          // Style tables
          table: ({ children }) => <ScrollableTable>{children}</ScrollableTable>,
          thead: ({ children }) => <thead className="border-b bg-muted/50">{children}</thead>,
          tbody: ({ children }) => <tbody>{children}</tbody>,
          tr: ({ children }) => <tr className="border-b last:border-0">{children}</tr>,
          th: ({ children }) => <th className="px-3 py-2 text-left font-medium">{children}</th>,
          td: ({ children }) => <td className="px-3 py-2">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export { MessageContent }
