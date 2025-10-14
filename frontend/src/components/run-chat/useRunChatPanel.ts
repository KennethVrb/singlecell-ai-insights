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
      tableUrl: msg.table_url,
      plotUrl: msg.plot_url,
      metricKey: msg.metric_key,
      tablePreviewStatus: "idle" as const,
      tablePreview: null,
      tablePreviewError: null,
      error: null,
    }))

    setMessages(convertedMessages)

    // Load table previews for messages with table URLs
    convertedMessages.forEach((msg) => {
      if (msg.tableUrl && msg.role === "assistant") {
        loadTablePreview(msg.id, msg.tableUrl)
      }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

function buildTablePreview(csvText: string): TablePreview {
  const lines = csvText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  if (lines.length === 0) {
    return { headers: [], rows: [] }
  }

  const [headerLine, ...rest] = lines

  // Detect delimiter (tab or comma)
  const delimiter = headerLine.includes("\t") ? "\t" : ","

  const headers = parseCsvLine(headerLine, delimiter)
  const rows = rest.slice(0, 10).map((line) => parseCsvLine(line, delimiter))

  // Limit to first 8 columns to prevent overflow
  const maxColumns = 8
  const limitedHeaders = headers.slice(0, maxColumns)
  const limitedRows = rows.map((row) => row.slice(0, maxColumns))

  return {
    headers: limitedHeaders,
    rows: limitedRows,
  }
}

function parseCsvLine(line: string, delimiter = ","): string[] {
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

    if (character === delimiter && !inQuotes) {
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
