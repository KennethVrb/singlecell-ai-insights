import { useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { FormEvent } from "react"

import { ApiError } from "@/api/client"
import type { ChatMessage as ApiChatMessage } from "@/api/runs"
import {
  useConversationHistoryQuery,
  useDeleteConversationHistoryMutation,
  useRunChatMutation,
} from "@/api/runs"
import { GlobalErrorDialogContext } from "@/providers/global-error/global-error-dialog-context"

import type { ChatMessage, UseRunChatPanelResult } from "./types"

type UseRunChatPanelOptions = {
  runId: number | null | undefined
  enabled: boolean
}

function useRunChatPanel({ runId, enabled }: UseRunChatPanelOptions): UseRunChatPanelResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [textareaValue, setTextareaValue] = useState("")
  const chatMutation = useRunChatMutation()
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
      error: null,
    }))

    setMessages(convertedMessages)
  }, [historyData])

  const composerDisabled = useMemo(() => {
    return !enabled || !Number.isFinite(runId) || chatMutation.isPending
  }, [enabled, runId, chatMutation.isPending])

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
        },
      ])

      setTextareaValue("")

      chatMutation.mutate(
        { pk: numericRunId, question },
        {
          onSuccess: (data: ApiChatMessage) => {
            updateMessage(assistantMessageId, (message) => ({
              ...message,
              status: "complete",
              content: data.content,
              citations: data.citations ?? [],
              notes: data.notes ?? [],
              metricKey: data.metric_key ?? null,
            }))
          },
          onError: (error) => {
            const errorMessage =
              error instanceof Error ? error.message : "Unable to fetch agent response."

            updateMessage(assistantMessageId, (message) => ({
              ...message,
              status: "error",
              error: errorMessage,
            }))

            if (globalErrorDialog) {
              const status = error instanceof ApiError ? error.status : 0
              const detail = error instanceof ApiError ? error.data : null

              globalErrorDialog.showError({
                status,
                endpoint: `/runs/${numericRunId}/chat/`,
                message: errorMessage,
                detail,
              })
            }
          },
        },
      )
    },
    [
      chatMutation,
      composerDisabled,
      enabled,
      globalErrorDialog,
      runId,
      textareaValue,
      updateMessage,
    ],
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
    isSubmitting: chatMutation.isPending,
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
