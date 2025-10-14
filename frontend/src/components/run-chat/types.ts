import type { Dispatch, FormEvent, SetStateAction } from "react"

type ChatRole = "user" | "assistant"

type ChatMessageStatus = "pending" | "complete" | "error"

type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  status: ChatMessageStatus
  citations: string[]
  notes: string[]
  metricKey: string | null
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

export type { ChatMessage, UseRunChatPanelResult }
