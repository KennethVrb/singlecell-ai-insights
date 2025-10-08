import { requestJSON } from "./client"

type RunSummary = {
  run_id: string
  name: string
  status: string
  pipeline: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  s3_report_key: string
}

async function listRuns(accessToken: string | null) {
  return await requestJSON<RunSummary[]>({
    endpoint: "/runs/",
    accessToken,
  })
}

export { listRuns }
export type { RunSummary }
