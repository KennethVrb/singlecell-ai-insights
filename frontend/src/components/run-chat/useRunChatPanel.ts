import { useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { FormEvent } from "react"

import { ApiError } from "@/api/client"
import type { ChatMessage as ApiChatMessage } from "@/api/runs"
import { useConversationHistoryQuery, useRunChatMutation } from "@/api/runs"
import { GlobalErrorDialogContext } from "@/providers/global-error/global-error-dialog-context"

import type { ChatMessage, TablePreviewData, UseRunChatPanelResult } from "./types"

type UseRunChatPanelOptions = {
  runId: number | null | undefined
  enabled: boolean
}

type TablePreview = Exclude<TablePreviewData, null>

function useRunChatPanel({ runId, enabled }: UseRunChatPanelOptions): UseRunChatPanelResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [textareaValue, setTextareaValue] = useState("")
  const chatMutation = useRunChatMutation()
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
      tableUrl: msg.table_url,
      plotUrl: msg.plot_url,
      metricKey: msg.metric_key,
      tablePreviewStatus: "idle" as const,
      tablePreview: null,
      tablePreviewError: null,
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

  const loadTablePreview = useCallback(
    async (messageId: string, tableUrl: string) => {
      updateMessage(messageId, (message) => ({
        ...message,
        tablePreviewStatus: "loading",
        tablePreviewError: null,
      }))

      try {
        const response = await fetch(tableUrl, {
          method: "GET",
          mode: "cors",
          credentials: "omit",
        })
        if (!response.ok) {
          throw new Error(`Unable to load CSV preview (status ${response.status}).`)
        }
        const text = await response.text()
        const preview = buildTablePreview(text)
        updateMessage(messageId, (message) => ({
          ...message,
          tablePreviewStatus: "ready",
          tablePreview: preview,
        }))
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unable to load table preview."
        updateMessage(messageId, (message) => ({
          ...message,
          tablePreviewStatus: "error",
          tablePreviewError: errorMessage,
        }))
      }
    },
    [updateMessage],
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
          tableUrl: null,
          plotUrl: null,
          metricKey: null,
          tablePreviewStatus: "idle",
          tablePreview: null,
          tablePreviewError: null,
          error: null,
        },
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          status: "pending",
          citations: [],
          notes: [],
          tableUrl: null,
          plotUrl: null,
          metricKey: null,
          tablePreviewStatus: "idle",
          tablePreview: null,
          tablePreviewError: null,
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
              tableUrl: data.table_url ?? null,
              plotUrl: data.plot_url ?? null,
              metricKey: data.metric_key ?? null,
              tablePreviewStatus: data.table_url ? "loading" : "idle",
            }))

            if (data.table_url) {
              loadTablePreview(assistantMessageId, data.table_url)
            }
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
      loadTablePreview,
      runId,
      textareaValue,
      updateMessage,
    ],
  )

  return {
    messages,
    textareaValue,
    setTextareaValue,
    handleSubmit,
    isSubmitting: chatMutation.isPending,
    composerDisabled,
  }
}

function buildTablePreview(csvText: string): TablePreview {
  const lines = csvText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  if (lines.length === 0) {
    return { headers: [], rows: [] }
  }

  const [headerLine, ...rest] = lines
  const headers = parseCsvLine(headerLine)
  const rows = rest.slice(0, 10).map((line) => parseCsvLine(line))

  return {
    headers,
    rows,
  }
}

function parseCsvLine(line: string): string[] {
  const cells: string[] = []
  let current = ""
  let inQuotes = false

  for (let index = 0; index < line.length; index += 1) {
    const character = line[index]

    if (character === '"') {
      const nextCharacter = line[index + 1]
      if (inQuotes && nextCharacter === '"') {
        current += '"'
        index += 1
      } else {
        inQuotes = !inQuotes
      }
      continue
    }

    if (character === "," && !inQuotes) {
      cells.push(current.trim())
      current = ""
      continue
    }

    current += character
  }

  cells.push(current.trim())

  return cells
}

function createMessageId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }

  return Math.random().toString(36).slice(2)
}

export { useRunChatPanel }
