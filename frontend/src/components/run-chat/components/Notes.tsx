function Notes({ notes }: { notes: string[] }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Notes</p>
      <ul className="list-disc space-y-1 pl-4 text-sm">
        {notes.map((note, index) => (
          <li key={index}>{note}</li>
        ))}
      </ul>
    </div>
  )
}

export { Notes }
