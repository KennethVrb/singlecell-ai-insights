import type { Dispatch, FormEvent, SetStateAction } from "react"

type ChatRole = "user" | "assistant"

type ChatMessageStatus = "pending" | "complete" | "error"

type TablePreviewStatus = "idle" | "loading" | "ready" | "error"

type TablePreviewData = {
  headers: string[]
  rows: string[][]
} | null

type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  status: ChatMessageStatus
  citations: string[]
  notes: string[]
  tableUrl: string | null
  plotUrl: string | null
  metricKey: string | null
  tablePreviewStatus: TablePreviewStatus
  tablePreview: TablePreviewData
  tablePreviewError: string | null
  error: string | null
}

type UseRunChatPanelResult = {
  messages: ChatMessage[]
  textareaValue: string
  setTextareaValue: Dispatch<SetStateAction<string>>
  handleSubmit: (event: FormEvent<HTMLFormElement>) => void
  isSubmitting: boolean
  composerDisabled: boolean
  handleDeleteHistory: () => void
  isDeletingHistory: boolean
}

export type { ChatMessage, TablePreviewData, TablePreviewStatus, UseRunChatPanelResult }
