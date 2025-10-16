import { Button } from "@/components/ui/button"

type SuggestedQuestion = {
  text: string
  icon: string
  category: string
}

const SUGGESTED_QUESTIONS: SuggestedQuestion[] = [
  {
    text: "Which samples have high duplication rates?",
    icon: "📊",
    category: "comparison",
  },
  {
    text: "Are there any outliers in this run?",
    icon: "🔍",
    category: "analysis",
  },
  {
    text: "What's the average GC content?",
    icon: "📈",
    category: "metrics",
  },
  {
    text: "Show me quality score distribution",
    icon: "📉",
    category: "visualization",
  },
  {
    text: "Which samples failed QC tests?",
    icon: "⚠️",
    category: "troubleshooting",
  },
]

type SuggestedQuestionsProps = {
  onSelect: (question: string) => void
  disabled?: boolean
}

function SuggestedQuestions({ onSelect, disabled = false }: SuggestedQuestionsProps) {
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-muted-foreground">Try asking the agent:</p>
      <div className="grid gap-2 sm:grid-cols-2">
        {SUGGESTED_QUESTIONS.map((q) => (
          <Button
            key={q.text}
            variant="outline"
            size="lg"
            onClick={() => onSelect(q.text)}
            disabled={disabled}
            className="justify-start text-left text-base"
          >
            <span className="mr-2">{q.icon}</span>
            <span className="truncate">{q.text}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}

export { SuggestedQuestions }
