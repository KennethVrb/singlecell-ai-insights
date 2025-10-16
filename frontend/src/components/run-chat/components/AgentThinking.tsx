import { CheckCircle2, Loader2 } from "lucide-react"

import type { AgentStatus, AgentStep } from "../types"

type AgentThinkingProps = {
  agentStatus: AgentStatus
}

const STEP_LABELS: Record<string, string> = {
  load: "Loading MultiQC data",
  index: "Building vector index",
  analyze: "Analyzing question",
  table: "Generating data table",
  plot: "Creating visualization",
  synthesize: "Synthesizing answer",
}

function AgentThinking({ agentStatus }: AgentThinkingProps) {
  const { currentStep, completedSteps, message } = agentStatus

  // Only show steps that have been completed or are currently running
  const relevantSteps = Object.entries(STEP_LABELS).filter(([step]) => {
    const isCompleted = completedSteps.includes(step as AgentStep)
    const isCurrent = currentStep === step
    return isCompleted || isCurrent
  })

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
        <span className="text-sm font-medium text-foreground">Agent is thinking...</span>
      </div>

      <div className="space-y-1.5 text-xs">
        {relevantSteps.map(([step, label]) => {
          const isCompleted = completedSteps.includes(step as AgentStep)
          const isCurrent = currentStep === step

          return (
            <div
              key={step}
              className="flex items-center gap-2 text-muted-foreground transition-colors"
            >
              {isCompleted ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                  <span className="text-green-600">{label}</span>
                </>
              ) : isCurrent ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-600" />
                  <span className="text-blue-600">{message || label}</span>
                </>
              ) : null}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export { AgentThinking }
