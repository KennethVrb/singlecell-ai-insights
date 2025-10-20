import { useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"

import logo from "@/assets/logo.svg"

function LandingPage() {
  const navigate = useNavigate()

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-background to-muted px-6 py-10 text-foreground">
      <div className="flex max-w-3xl flex-col items-center space-y-8 text-center">
        <img src={logo} alt="SingleCell AI Insights" className="h-24 w-24" />

        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight">SingleCell AI Insights</h1>
          <p className="text-xl text-muted-foreground">
            Intelligent analysis for genomics workflows
          </p>
        </div>

        <div className="space-y-4">
          <p className="max-w-2xl text-lg text-muted-foreground">
            Transform hours of manual MultiQC report analysis into 30-second conversations. Our AI
            agent connects to AWS HealthOmics, analyzes quality metrics, and provides instant
            insights for your single-cell RNA-seq pipelines.
          </p>
        </div>

        <div className="flex gap-4">
          <Button size="lg" className="text-lg px-8 py-6" onClick={() => navigate("/login")}>
            Get Started
          </Button>
        </div>
      </div>
    </main>
  )
}

export default LandingPage
