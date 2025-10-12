import { type ReactNode, useCallback, useMemo, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

import { GlobalErrorDialogContext } from "./global-error-dialog-context"
import type {
  GlobalErrorDetail,
  GlobalErrorDialogContextValue,
} from "./global-error-dialog-context"

type GlobalErrorDialogProviderProps = {
  children: ReactNode
}

function GlobalErrorDialogProvider({ children }: GlobalErrorDialogProviderProps) {
  const [errorDetail, setErrorDetail] = useState<GlobalErrorDetail | null>(null)

  const showError = useCallback((detail: GlobalErrorDetail) => {
    setErrorDetail(detail)
  }, [])

  const dismiss = useCallback(() => {
    setErrorDetail(null)
  }, [])

  const contextValue = useMemo<GlobalErrorDialogContextValue>(() => {
    return {
      showError,
      dismiss,
    }
  }, [dismiss, showError])

  const isOpen = Boolean(errorDetail)

  const detailContent = useMemo(() => {
    if (!errorDetail) {
      return null
    }

    const { detail } = errorDetail

    if (detail === null || detail === undefined) {
      return null
    }

    if (typeof detail === "string") {
      return detail
    }

    try {
      return JSON.stringify(detail, null, 2)
    } catch (serializationError) {
      console.error("Failed to serialize API error detail", serializationError)
      return null
    }
  }, [errorDetail])

  return (
    <GlobalErrorDialogContext.Provider value={contextValue}>
      {children}
      <Dialog open={isOpen} onOpenChange={(open) => (open ? undefined : dismiss())}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Something went wrong</DialogTitle>
            {errorDetail ? (
              <DialogDescription>
                {errorDetail.message}{" "}
                <span className="block text-xs text-muted-foreground">
                  {errorDetail.status} {errorDetail.endpoint}
                </span>
              </DialogDescription>
            ) : null}
          </DialogHeader>
          {detailContent ? (
            <pre className="max-h-48 overflow-auto rounded bg-muted p-3 text-xs text-muted-foreground">
              {detailContent}
            </pre>
          ) : null}
          <DialogFooter>
            <Button variant="brand" onClick={dismiss}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </GlobalErrorDialogContext.Provider>
  )
}

export { GlobalErrorDialogProvider }
