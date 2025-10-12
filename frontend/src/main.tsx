import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router-dom"

import { AuthProvider } from "@/providers/auth/AuthProvider"
import { GlobalErrorDialogProvider } from "@/providers/global-error/GlobalErrorDialogProvider"
import { QueryProvider } from "@/providers/QueryProvider"
import { router } from "./routes"
import "./index.css"

const container = document.getElementById("root")

if (container) {
  createRoot(container).render(
    <StrictMode>
      <AuthProvider>
        <QueryProvider>
          <GlobalErrorDialogProvider>
            <RouterProvider router={router} />
          </GlobalErrorDialogProvider>
        </QueryProvider>
      </AuthProvider>
    </StrictMode>,
  )
}
