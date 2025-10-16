import type { Dispatch, FormEvent, SetStateAction } from "react"

type ChatRole = "user" | "assistant"

type ChatMessageStatus = "pending" | "complete" | "error"

type AgentStep = "load" | "index" | "analyze" | "table" | "plot" | "synthesize"

type AgentStatus = {
  currentStep: AgentStep | null
  completedSteps: AgentStep[]
  message: string
}

type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  status: ChatMessageStatus
  citations: string[]
  notes: string[]
  metricKey: string | null
  error: string | null
  agentStatus?: AgentStatus
  confidence?: number
  confidenceExplanation?: string
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

export type { AgentStep, AgentStatus, ChatMessage, UseRunChatPanelResult }
