import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import { Button } from "@/components/ui/button"
import "./index.css"

export function Root() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-6 py-10 text-foreground">
      <section className="space-y-2 text-center">
        <h1 className="text-3xl font-semibold">Radix Button Showcase</h1>
        <p className="text-muted-foreground">
          Try the button variants below to verify the shadcn/ui configuration.
        </p>
      </section>

      <div className="flex flex-wrap items-center justify-center gap-4">
        <Button>Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="link">Link style</Button>
      </div>
    </main>
  )
}

const container = document.getElementById("root")

if (container) {
  createRoot(container).render(
    <StrictMode>
      <Root />
    </StrictMode>,
  )
}
