import { useCallback, useContext, useEffect, useMemo, useRef } from "react"

import { ApiError } from "@/api/client"
import { useRunMultiqcReportMutation, useRunQuery } from "@/api/runs"
import { GlobalErrorDialogContext } from "@/providers/global-error/global-error-dialog-context"

function useRunDetail(runIdParam?: string) {
  const numericRunId = runIdParam ? Number.parseInt(runIdParam, 10) : NaN
  const { data: run, isLoading, isError, error } = useRunQuery(numericRunId)
  const multiqcReportMutation = useRunMultiqcReportMutation()
  const globalErrorDialog = useContext(GlobalErrorDialogContext)
  const hasShownError = useRef(false)

  useEffect(() => {
    if (!globalErrorDialog) {
      return
    }

    if (!isError) {
      hasShownError.current = false
      return
    }

    if (!error || hasShownError.current) {
      return
    }

    const endpoint = Number.isFinite(numericRunId) ? `/runs/${numericRunId}/` : "/runs/"
    const message = error instanceof Error ? error.message : "Unable to load run."
    const status = error instanceof ApiError ? error.status : 0
    const detail = error instanceof ApiError ? error.data : null

    globalErrorDialog.showError({
      status,
      endpoint,
      message,
      detail,
    })

    hasShownError.current = true
  }, [error, globalErrorDialog, isError, numericRunId])

  const isRunFailed = useMemo(() => {
    if (!run?.status) {
      return false
    }

    return ["FAILED", "ERROR"].includes(run.status.toUpperCase())
  }, [run?.status])

  const isChatReady = useMemo(() => {
    if (!run?.status) {
      return false
    }

    return ["COMPLETED", "SUCCEEDED"].includes(run.status.toUpperCase())
  }, [run?.status])

  const isMultiqcAvailable = useMemo(() => {
    return run?.status === "COMPLETED" && Boolean(run?.output_dir_bucket && run?.output_dir_key)
  }, [run?.output_dir_bucket, run?.output_dir_key, run?.status])

  const handleDownloadMultiqc = useCallback(() => {
    if (!run || !isMultiqcAvailable || multiqcReportMutation.isPending) {
      return
    }

    multiqcReportMutation.mutate(run.pk, {
      onSuccess: ({ multiqc_report_url }) => {
        window.open(multiqc_report_url, "_blank", "noopener,noreferrer")
      },
      onError: (mutationError) => {
        if (!globalErrorDialog) {
          return
        }

        const status = mutationError instanceof ApiError ? mutationError.status : 0
        const detail = mutationError instanceof ApiError ? mutationError.data : null
        const message =
          mutationError instanceof Error
            ? mutationError.message
            : "Unable to load the MultiQC report."

        const endpoint = `/runs/${run.pk}/multiqc-report/`

        globalErrorDialog.showError({
          status,
          endpoint,
          message,
          detail,
        })
      },
    })
  }, [globalErrorDialog, isMultiqcAvailable, multiqcReportMutation, run])

  return {
    run,
    isLoading,
    isChatReady,
    isRunFailed,
    isMultiqcAvailable,
    isMultiqcPending: multiqcReportMutation.isPending,
    handleDownloadMultiqc,
  }
}

export { useRunDetail }
