export function formatDateTime(value?: string | null) {
  if (!value) {
    return "—"
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return "—"
  }

  return parsed.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  })
}
