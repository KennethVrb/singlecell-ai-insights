function Citations({ citations }: { citations: string[] }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Citations
      </span>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation) => (
          <span
            key={citation}
            className="rounded-md border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium uppercase tracking-wide text-primary"
          >
            {citation}
          </span>
        ))}
      </div>
    </div>
  )
}

export { Citations }
