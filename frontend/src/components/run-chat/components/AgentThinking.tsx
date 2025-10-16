import { CheckCircle2, Loader2 } from "lucide-react"

import type { AgentStatus, AgentStep } from "../types"

type AgentThinkingProps = {
  agentStatus: AgentStatus
}

function AgentThinking({ agentStatus }: AgentThinkingProps) {
  const { currentStep, completedSteps, message, stepMessages } = agentStatus

  // Get all steps that have been seen (either completed or current)
  const allSteps = [...completedSteps]
  if (currentStep && !allSteps.includes(currentStep)) {
    allSteps.push(currentStep)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
        <span className="text-sm font-medium text-foreground">
          {message || "Agent is thinking..."}
        </span>
      </div>

      <div className="space-y-1.5 text-xs">
        {allSteps.map((step) => {
          const isCompleted = completedSteps.includes(step)
          const isCurrent = currentStep === step
          const stepMessage = stepMessages[step] || step

          return (
            <div
              key={step}
              className="flex items-center gap-2 text-muted-foreground transition-colors"
            >
              {isCompleted ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                  <span className="text-green-600">{stepMessage}</span>
                </>
              ) : isCurrent ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-600" />
                  <span className="text-blue-600">{stepMessage}</span>
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
