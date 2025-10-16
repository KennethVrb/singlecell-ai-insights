import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { requestJSON, requestStream } from "./client"
import { API_ENDPOINTS } from "./endpoints"

type ChatMessage = {
  id: number
  role: "user" | "assistant"
  content: string
  citations: string[]
  notes: string[]
  metric_key: string | null
  confidence?: number
  confidence_explanation?: string
  created_at: string
}

type ConversationHistory = {
  messages: ChatMessage[]
}

type StreamEvent =
  | { type: "status"; step: string; message: string }
  | {
      type: "answer"
      content: {
        answer: string
        citations: string[]
        notes: string[]
        metric_key: string | null
        confidence?: number
        confidence_explanation?: string
      }
    }
  | { type: "error"; message: string }
  | { type: "message_id"; id: number }

type StreamCallbacks = {
  onStatus?: (step: string, message: string) => void
  onAnswer?: (content: {
    answer: string
    citations: string[]
    notes: string[]
    metric_key: string | null
    confidence?: number
    confidence_explanation?: string
  }) => void
  onError?: (message: string) => void
  onComplete?: () => void
}

async function getConversationHistory(pk: number) {
  return await requestJSON<ConversationHistory>({
    endpoint: API_ENDPOINTS.RUNS.CHAT(pk),
  })
}

async function deleteConversationHistory(pk: number) {
  return await requestJSON<void>({
    endpoint: API_ENDPOINTS.RUNS.CHAT(pk),
    method: "DELETE",
  })
}

async function streamChat(pk: number, question: string, callbacks: StreamCallbacks) {
  // Use requestStream which handles auth refresh automatically
  const response = await requestStream({
    endpoint: API_ENDPOINTS.RUNS.CHAT_STREAM(pk),
    method: "POST",
    body: { question },
  })

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) {
    throw new Error("No response body")
  }

  try {
    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        callbacks.onComplete?.()
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split("\n")

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6)

          if (data === "[DONE]") {
            callbacks.onComplete?.()
            break
          }

          try {
            const parsed: StreamEvent = JSON.parse(data)

            if (parsed.type === "status") {
              callbacks.onStatus?.(parsed.step, parsed.message)
            } else if (parsed.type === "answer") {
              callbacks.onAnswer?.(parsed.content)
            } else if (parsed.type === "error") {
              callbacks.onError?.(parsed.message)
            }
          } catch (error) {
            console.error("Failed to parse SSE data:", error)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

function useConversationHistoryQuery(pk: number | null | undefined, enabled: boolean) {
  const isValidPk = typeof pk === "number" && Number.isFinite(pk)

  return useQuery({
    queryKey: ["conversation", isValidPk ? pk : "invalid"],
    queryFn: () => {
      if (!isValidPk) {
        throw new Error("Invalid run identifier")
      }

      return getConversationHistory(pk as number)
    },
    enabled: isValidPk && enabled,
  })
}

function useDeleteConversationHistoryMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (pk: number) => await deleteConversationHistory(pk),
    onSuccess: (_, pk) => {
      queryClient.setQueryData(["conversation", pk], { messages: [] })
    },
  })
}

export { streamChat, useConversationHistoryQuery, useDeleteConversationHistoryMutation }
export type { ChatMessage, ConversationHistory, StreamCallbacks, StreamEvent }
