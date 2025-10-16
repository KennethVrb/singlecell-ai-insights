import { Info } from "lucide-react"

import { Progress } from "@/components/ui/progress"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

import { AgentThinking } from "./AgentThinking"
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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-600"
    if (confidence >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return "High confidence"
    if (confidence >= 60) return "Moderate confidence"
    return "Low confidence"
  }

  return (
    <div className={cn("flex w-full break-word", isUser ? "justify-end" : "justify-start")}>
      <div className={bubbleClasses}>
        <div className="space-y-3">
          {message.status === "pending" && message.agentStatus ? (
            <AgentThinking agentStatus={message.agentStatus} />
          ) : (
            <>
              <MessageContent message={message} />
              {message.notes?.length ? <Notes notes={message.notes} /> : null}

              {/* Confidence indicator for assistant messages */}
              {message.role === "assistant" &&
                message.confidence != null &&
                message.status === "complete" && (
                  <div className="flex items-center gap-3 border-t pt-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Confidence:</span>
                      <Progress value={message.confidence} className="h-1.5 w-16" />
                      <span className={cn("font-medium", getConfidenceColor(message.confidence))}>
                        {message.confidence}%
                      </span>
                    </div>

                    {message.confidenceExplanation && (
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info className="h-3 w-3 cursor-help text-muted-foreground" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <p className="text-xs">{message.confidenceExplanation}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    )}

                    <span
                      className={cn(
                        "ml-auto text-xs font-medium",
                        getConfidenceColor(message.confidence),
                      )}
                    >
                      {getConfidenceLabel(message.confidence)}
                    </span>
                  </div>
                )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export { ChatMessageBubble }
export type { ChatMessageProps }
