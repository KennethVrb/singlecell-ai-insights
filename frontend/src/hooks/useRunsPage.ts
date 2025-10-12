import { useCallback, useContext, useEffect, useMemo, useRef } from "react"

import { ApiError } from "@/api/client"
import { useRunsQuery, useSyncRuns } from "@/api/runs"
import { GlobalErrorDialogContext } from "@/providers/global-error/global-error-dialog-context"

function useRunsPage() {
  const { data: runs, isLoading, isError, error } = useRunsQuery()
  const { mutate: syncRuns, isPending: isSyncing } = useSyncRuns()
  const globalErrorDialog = useContext(GlobalErrorDialogContext)
  const hasShownRunsError = useRef(false)

  useEffect(() => {
    if (!globalErrorDialog) {
      return
    }

    if (!isError) {
      hasShownRunsError.current = false
      return
    }

    if (!error || hasShownRunsError.current) {
      return
    }

    const status = error instanceof ApiError ? error.status : 0
    const detail = error instanceof ApiError ? error.data : null
    const message = error instanceof Error ? error.message : "Unable to load runs."

    globalErrorDialog.showError({
      status,
      endpoint: "/runs/",
      message,
      detail,
    })

    hasShownRunsError.current = true
  }, [error, globalErrorDialog, isError])

  const handleSyncRuns = useCallback(() => {
    syncRuns(undefined, {
      onError: (mutationError) => {
        if (!globalErrorDialog) {
          return
        }

        const status = mutationError instanceof ApiError ? mutationError.status : 0
        const detail = mutationError instanceof ApiError ? mutationError.data : null
        const message =
          mutationError instanceof Error
            ? mutationError.message
            : "Unable to refresh runs from HealthOmics."

        globalErrorDialog.showError({
          status,
          endpoint: "/runs/?refresh=true",
          message,
          detail,
        })
      },
    })
  }, [globalErrorDialog, syncRuns])

  const runItems = useMemo(() => runs ?? [], [runs])

  return {
    runItems,
    isLoading,
    isError,
    error,
    isSyncing,
    handleSyncRuns,
  }
}

export { useRunsPage }
