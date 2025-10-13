import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { requestJSON } from "./client"

type RunSummary = {
  pk: number
  run_id: string
  name: string
  status: string
  pipeline: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  output_dir_bucket: string
  output_dir_key: string
}

type Run = RunSummary & {
  output_dir_bucket: string
  output_dir_key: string
}

type RunMultiqcReport = {
  multiqc_report_url: string
}

type ChatMessage = {
  id: number
  role: "user" | "assistant"
  content: string
  citations: string[]
  notes: string[]
  table_url: string | null
  plot_url: string | null
  metric_key: string | null
  created_at: string
}

type ConversationHistory = {
  messages: ChatMessage[]
}

async function listRuns(refresh?: boolean) {
  let params = {}

  if (refresh) {
    params = { refresh: "true" }
  }

  return await requestJSON<RunSummary[]>({
    endpoint: "/runs/",
    params,
  })
}

async function getRun(pk: number) {
  return await requestJSON<Run>({
    endpoint: `/runs/${pk}/`,
  })
}

async function getRunMultiqcReport(pk: number) {
  return await requestJSON<RunMultiqcReport>({
    endpoint: `/runs/${pk}/multiqc-report/`,
  })
}

async function getConversationHistory(pk: number) {
  return await requestJSON<ConversationHistory>({
    endpoint: `/runs/${pk}/chat/`,
  })
}

async function runChat(pk: number, question: string) {
  return await requestJSON<ChatMessage>({
    endpoint: `/runs/${pk}/chat/`,
    method: "POST",
    body: { question },
  })
}

async function deleteConversationHistory(pk: number) {
  return await requestJSON<void>({
    endpoint: `/runs/${pk}/chat/`,
    method: "DELETE",
  })
}

function useRunsQuery(refresh?: boolean) {
  return useQuery({
    queryKey: ["runs"],
    queryFn: () => listRuns(refresh),
  })
}

function useSyncRuns() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => await listRuns(true),
    onSuccess: (data) => {
      queryClient.setQueryData(["runs"], data)
    },
  })
}

function useRunQuery(pk: number | null | undefined) {
  const isValidPk = typeof pk === "number" && Number.isFinite(pk)

  return useQuery({
    queryKey: ["run", isValidPk ? pk : "invalid"],
    queryFn: () => {
      if (!isValidPk) {
        throw new Error("Invalid run identifier")
      }

      return getRun(pk as number)
    },
    enabled: isValidPk,
  })
}

function useRunMultiqcReportMutation() {
  return useMutation({
    mutationFn: async (pk: number) => await getRunMultiqcReport(pk),
  })
}

function useRunChatMutation() {
  return useMutation({
    mutationFn: async ({ pk, question }: { pk: number; question: string }) =>
      await runChat(pk, question),
  })
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

export {
  useRunsQuery,
  useRunQuery,
  useRunMultiqcReportMutation,
  useSyncRuns,
  useRunChatMutation,
  useConversationHistoryQuery,
  useDeleteConversationHistoryMutation,
}
export type { RunSummary, Run, RunMultiqcReport, ChatMessage }
