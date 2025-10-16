import { useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { FormEvent } from "react"

import { ApiError } from "@/api/client"
import type { ChatMessage as ApiChatMessage } from "@/api/chat"
import {
  streamChat,
  useConversationHistoryQuery,
  useDeleteConversationHistoryMutation,
} from "@/api/chat"
import { GlobalErrorDialogContext } from "@/providers/global-error/global-error-dialog-context"

import type { AgentStep, ChatMessage, UseRunChatPanelResult } from "./types"

type UseRunChatPanelOptions = {
  runId: number | null | undefined
  enabled: boolean
}

function useRunChatPanel({ runId, enabled }: UseRunChatPanelOptions): UseRunChatPanelResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [textareaValue, setTextareaValue] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const deleteMutation = useDeleteConversationHistoryMutation()
  const globalErrorDialog = useContext(GlobalErrorDialogContext)

  // Load conversation history on mount
  const { data: historyData } = useConversationHistoryQuery(runId, enabled)

  // Load conversation history into messages
  useEffect(() => {
    if (!historyData?.messages) return

    const convertedMessages: ChatMessage[] = historyData.messages.map((msg: ApiChatMessage) => ({
      id: String(msg.id),
      role: msg.role,
      content: msg.content,
      status: "complete" as const,
      citations: msg.citations,
      notes: msg.notes,
      metricKey: msg.metric_key,
      confidence: msg.confidence,
      confidenceExplanation: msg.confidence_explanation,
      error: null,
    }))

    setMessages(convertedMessages)
  }, [historyData])

  const composerDisabled = useMemo(() => {
    return !enabled || !Number.isFinite(runId) || isStreaming
  }, [enabled, runId, isStreaming])

  const updateMessage = useCallback(
    (messageId: string, updater: (previous: ChatMessage) => ChatMessage) => {
      setMessages((previous) =>
        previous.map((message) => {
          if (message.id !== messageId) {
            return message
          }
          return updater(message)
        }),
      )
    },
    [],
  )

  const handleSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()

      if (!enabled || composerDisabled) {
        return
      }

      const question = textareaValue.trim()
      if (question.length === 0) {
        return
      }

      if (!Number.isFinite(runId)) {
        return
      }

      const numericRunId = Number(runId)
      const userMessageId = createMessageId()
      const assistantMessageId = createMessageId()

      // Add user message and pending assistant message
      setMessages((previous) => [
        ...previous,
        {
          id: userMessageId,
          role: "user",
          content: question,
          status: "complete",
          citations: [],
          notes: [],
          metricKey: null,
          error: null,
        },
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          status: "pending",
          citations: [],
          notes: [],
          metricKey: null,
          error: null,
          agentStatus: {
            currentStep: null,
            completedSteps: [],
            message: "Initializing...",
          },
        },
      ])

      setTextareaValue("")
      setIsStreaming(true)

      // Use streamChat API
      streamChat(numericRunId, question, {
        onStatus: (step, message) => {
          updateMessage(assistantMessageId, (msg) => {
            const currentSteps = msg.agentStatus?.completedSteps ?? []
            // Only add step if it's not already in the list
            const newCompletedSteps = currentSteps.includes(step as AgentStep)
              ? currentSteps
              : [...currentSteps, step as AgentStep]

            return {
              ...msg,
              agentStatus: {
                currentStep: step as AgentStep,
                completedSteps: newCompletedSteps,
                message,
              },
            }
          })
        },
        onAnswer: (content) => {
          updateMessage(assistantMessageId, (msg) => ({
            ...msg,
            status: "complete",
            content: content.answer,
            citations: content.citations ?? [],
            notes: content.notes ?? [],
            metricKey: content.metric_key ?? null,
            confidence: content.confidence,
            confidenceExplanation: content.confidence_explanation,
            agentStatus: undefined,
          }))
        },
        onError: (errorMessage) => {
          updateMessage(assistantMessageId, (msg) => ({
            ...msg,
            status: "error",
            error: errorMessage,
            agentStatus: undefined,
          }))
          setIsStreaming(false)
        },
        onComplete: () => {
          setIsStreaming(false)
        },
      }).catch((error) => {
        updateMessage(assistantMessageId, (msg) => ({
          ...msg,
          status: "error",
          error: "Connection to agent failed",
          agentStatus: undefined,
        }))
        setIsStreaming(false)

        if (globalErrorDialog) {
          globalErrorDialog.showError({
            status: 0,
            endpoint: `/runs/${numericRunId}/chat/stream/`,
            message: error instanceof Error ? error.message : "Streaming connection failed",
            detail: null,
          })
        }
      })
    },
    [composerDisabled, enabled, globalErrorDialog, runId, textareaValue, updateMessage],
  )

  const handleDeleteHistory = useCallback(() => {
    if (!Number.isFinite(runId)) {
      return
    }

    const numericRunId = Number(runId)

    deleteMutation.mutate(numericRunId, {
      onSuccess: () => {
        setMessages([])
      },
      onError: (error) => {
        if (globalErrorDialog) {
          const status = error instanceof ApiError ? error.status : 0
          const detail = error instanceof ApiError ? error.data : null
          const errorMessage =
            error instanceof Error ? error.message : "Unable to delete conversation history."

          globalErrorDialog.showError({
            status,
            endpoint: `/runs/${numericRunId}/chat/`,
            message: errorMessage,
            detail,
          })
        }
      },
    })
  }, [runId, deleteMutation, globalErrorDialog])

  return {
    messages,
    textareaValue,
    setTextareaValue,
    handleSubmit,
    isSubmitting: isStreaming,
    composerDisabled,
    handleDeleteHistory,
    isDeletingHistory: deleteMutation.isPending,
  }
}

function createMessageId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }

  return Math.random().toString(36).slice(2)
}

export { useRunChatPanel }
