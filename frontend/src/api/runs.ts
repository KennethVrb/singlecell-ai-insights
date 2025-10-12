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
  metadata: Record<string, unknown> | null
  normalized_context: Record<string, unknown> | null
}

type RunMultiqcReport = {
  multiqc_report_url: string
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

export { useRunsQuery, useRunQuery, useRunMultiqcReportMutation, useSyncRuns }
export type { RunSummary, Run, RunMultiqcReport }
