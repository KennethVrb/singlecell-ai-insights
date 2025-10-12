import type { ReactNode } from "react"
import { CheckCircle2, Clock3, TriangleAlert } from "lucide-react"

import { cn } from "@/lib/utils"

const statusConfig: Record<string, { className: string; icon: ReactNode }> = {
  COMPLETED: {
    className: "status-badge status-badge-success",
    icon: <CheckCircle2 className="size-3.5" aria-hidden />,
  },
  SUCCEEDED: {
    className: "status-badge status-badge-success",
    icon: <CheckCircle2 className="size-3.5" aria-hidden />,
  },
  RUNNING: {
    className: "status-badge status-badge-warning",
    icon: <Clock3 className="size-3.5" aria-hidden />,
  },
  IN_PROGRESS: {
    className: "status-badge status-badge-warning",
    icon: <Clock3 className="size-3.5" aria-hidden />,
  },
  FAILED: {
    className: "status-badge status-badge-error",
    icon: <TriangleAlert className="size-3.5" aria-hidden />,
  },
  ERROR: {
    className: "status-badge status-badge-error",
    icon: <TriangleAlert className="size-3.5" aria-hidden />,
  },
}

type RunStatusBadgeProps = {
  status?: string | null
  className?: string
}

const formatStatus = (status?: string | null) => {
  if (!status) {
    return "Unknown"
  }

  return status
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/(^|\s)\w/g, (match) => match.toUpperCase())
}

export function RunStatusBadge({ status, className }: RunStatusBadgeProps) {
  const normalizedStatus = status?.toUpperCase() ?? ""
  const config = statusConfig[normalizedStatus]

  return (
    <span className={cn(config?.className ?? "status-badge", className)}>
      {config?.icon}
      {formatStatus(status)}
    </span>
  )
}
