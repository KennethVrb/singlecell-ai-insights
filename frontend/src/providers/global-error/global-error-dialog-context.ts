import { createContext } from "react"

type GlobalErrorDetail = {
  status: number
  endpoint: string
  message: string
  detail: unknown
}

type GlobalErrorDialogContextValue = {
  showError: (detail: GlobalErrorDetail) => void
  dismiss: () => void
}

const GlobalErrorDialogContext = createContext<GlobalErrorDialogContextValue | undefined>(undefined)

export { GlobalErrorDialogContext }
export type { GlobalErrorDetail, GlobalErrorDialogContextValue }
