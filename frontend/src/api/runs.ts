import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { requestJSON } from "./client"
import { API_ENDPOINTS } from "./endpoints"

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

type RunMetrics = {
  total_samples: number
  samples: Array<{
    name: string
    duplication_rate?: number
    gc_content?: number
    total_sequences?: number
  }>
}

async function listRuns(refresh?: boolean) {
  let params = {}

  if (refresh) {
    params = { refresh: "true" }
  }

  return await requestJSON<RunSummary[]>({
    endpoint: API_ENDPOINTS.RUNS.LIST,
    params,
  })
}

async function getRun(pk: number) {
  return await requestJSON<Run>({
    endpoint: API_ENDPOINTS.RUNS.DETAIL(pk),
  })
}

async function getRunMultiqcReport(pk: number) {
  return await requestJSON<RunMultiqcReport>({
    endpoint: API_ENDPOINTS.RUNS.MULTIQC_REPORT(pk),
  })
}

async function getRunMetrics(pk: number) {
  return await requestJSON<RunMetrics>({
    endpoint: API_ENDPOINTS.RUNS.METRICS(pk),
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

function useRunMetricsQuery(pk: number | null | undefined, enabled: boolean = true) {
  const isValidPk = typeof pk === "number" && Number.isFinite(pk)

  return useQuery({
    queryKey: ["run-metrics", isValidPk ? pk : "invalid"],
    queryFn: () => {
      if (!isValidPk) {
        throw new Error("Invalid run identifier")
      }

      return getRunMetrics(pk as number)
    },
    enabled: isValidPk && enabled,
  })
}

export { useRunsQuery, useRunQuery, useRunMultiqcReportMutation, useRunMetricsQuery, useSyncRuns }
export type { RunSummary, Run, RunMultiqcReport, RunMetrics }
