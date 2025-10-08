import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

export function Root() {
  return (
    <StrictMode>
      <div>singlecell-ai-insights frontend</div>
    </StrictMode>
  )
}

const container = document.getElementById("root")

if (container) {
  createRoot(container).render(<Root />)
}
