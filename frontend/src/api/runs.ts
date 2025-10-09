import { useQuery } from "@tanstack/react-query"

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
  s3_report_key: string
}

type Run = RunSummary & {
  metadata: Record<string, unknown> | null
  normalized_context: Record<string, unknown> | null
}

async function listRuns() {
  return await requestJSON<RunSummary[]>({
    endpoint: "/runs/",
  })
}

async function getRun(pk: number) {
  return await requestJSON<Run>({
    endpoint: `/runs/${pk}/`,
  })
}

function useRunsQuery() {
  return useQuery({
    queryKey: ["runs"],
    queryFn: listRuns,
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

export { useRunsQuery, useRunQuery }
export type { RunSummary, Run }
