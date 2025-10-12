import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowUpDown, ChevronLeft, ChevronRight, Filter, ChevronDown } from "lucide-react"

import type { RunSummary } from "@/api/runs"
import { RunStatusBadge } from "@/components/RunStatusBadge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { formatDateTime } from "@/lib/datetime"

const PAGE_SIZE_OPTIONS = [10, 20, 50]

function fuzzyMatch(value: string, query: string) {
  if (!query) {
    return true
  }

  const haystack = value.toLowerCase()
  const needle = query.toLowerCase()

  let searchIndex = 0
  for (const char of needle) {
    const foundIndex = haystack.indexOf(char, searchIndex)
    if (foundIndex === -1) {
      return false
    }

    searchIndex = foundIndex + 1
  }

  return true
}

type SortKey = "name" | "pipeline" | "status" | "created_at" | "completed_at"

type SortState = {
  key: SortKey
  direction: "asc" | "desc"
}

type RunsTableProps = {
  runs: RunSummary[]
  isLoading: boolean
  currentUserName?: string
}

export function RunsTable({ runs, isLoading, currentUserName }: RunsTableProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null)
  const [sort, setSort] = useState<SortState>({ key: "created_at", direction: "desc" })
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[0])
  const [page, setPage] = useState(1)

  const statusOptions = useMemo(() => {
    const unique = new Set(runs.map((run) => run.status ?? ""))
    return Array.from(unique)
      .filter((status) => Boolean(status))
      .sort()
  }, [runs])

  const filteredRuns = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase()

    return runs
      .filter((run) => {
        if (selectedStatus && run.status?.toUpperCase() !== selectedStatus.toUpperCase()) {
          return false
        }

        if (!normalizedSearch) {
          return true
        }

        const target = (run.name ?? run.run_id ?? "").toString()
        return fuzzyMatch(target, normalizedSearch)
      })
      .sort((a, b) => {
        const { key, direction } = sort
        const multiplier = direction === "asc" ? 1 : -1

        if (key === "created_at" || key === "completed_at") {
          const aValue = a[key] ?? ""
          const bValue = b[key] ?? ""
          return multiplier * aValue.localeCompare(bValue)
        }

        const aValue = (a[key] ?? "").toString().toLowerCase()
        const bValue = (b[key] ?? "").toString().toLowerCase()
        return multiplier * aValue.localeCompare(bValue)
      })
  }, [runs, searchTerm, selectedStatus, sort])

  const pageCount = Math.max(1, Math.ceil(filteredRuns.length / pageSize))
  const safePage = Math.min(page, pageCount)
  const paginatedRuns = useMemo(() => {
    const start = (safePage - 1) * pageSize
    return filteredRuns.slice(start, start + pageSize)
  }, [filteredRuns, pageSize, safePage])

  useEffect(() => {
    setPage(1)
  }, [searchTerm, selectedStatus, pageSize, sort, runs])

  const toggleSort = (key: SortKey) => {
    setSort((current) => {
      if (current.key === key) {
        const nextDirection = current.direction === "asc" ? "desc" : "asc"
        return { key, direction: nextDirection }
      }

      return { key, direction: key === "created_at" ? "desc" : "asc" }
    })
  }

  const renderSortTrigger = (label: string, key: SortKey) => {
    const isActive = sort.key === key
    const direction = isActive ? sort.direction : undefined

    return (
      <button
        type="button"
        onClick={() => toggleSort(key)}
        className="inline-flex items-center gap-1 hover:text-foreground"
        aria-label={`Sort by ${label}`}
      >
        {label}
        <ArrowUpDown
          className={`size-3.5 ${isActive ? "text-foreground" : "text-muted-foreground"}`}
          data-direction={direction}
        />
      </button>
    )
  }

  const onPageChange = (nextPage: number) => {
    setPage(Math.min(Math.max(1, nextPage), pageCount))
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-1 items-center gap-2">
          <Input
            placeholder="Search runs…"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            className="max-w-sm"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="flex items-center gap-1">
                <Filter className="size-3.5" aria-hidden />
                {selectedStatus ?? "All statuses"}
                <ChevronDown className="size-3" aria-hidden />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-[200px]">
              <DropdownMenuLabel>Status</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={() => setSelectedStatus(null)}>
                All statuses
              </DropdownMenuItem>
              {statusOptions.map((status) => (
                <DropdownMenuItem key={status} onSelect={() => setSelectedStatus(status)}>
                  {status}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Page size: {pageSize}
                <ChevronDown className="ml-1 size-3" aria-hidden />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Rows per page</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {PAGE_SIZE_OPTIONS.map((option) => (
                <DropdownMenuItem key={option} onSelect={() => setPageSize(option)}>
                  {option}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="hidden overflow-x-auto rounded-lg border border-border bg-card shadow-sm md:block">
        <Table className="min-w-[720px] text-sm">
          <TableHeader className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
            <TableRow>
              <TableHead className="px-4 py-3">{renderSortTrigger("Run", "name")}</TableHead>
              <TableHead className="px-4 py-3">
                {renderSortTrigger("Pipeline", "pipeline")}
              </TableHead>
              <TableHead className="px-4 py-3">{renderSortTrigger("Status", "status")}</TableHead>
              <TableHead className="px-4 py-3">
                {renderSortTrigger("Created", "created_at")}
              </TableHead>
              <TableHead className="px-4 py-3">
                {renderSortTrigger("Completed", "completed_at")}
              </TableHead>
              <TableHead className="px-4 py-3 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                  <div className="flex items-center justify-center gap-2">
                    <Spinner />
                    <span>Loading runs…</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : paginatedRuns.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                  {runs.length === 0
                    ? "No runs available yet. Try refreshing or check back later."
                    : "No runs match the current filters."}
                </TableCell>
              </TableRow>
            ) : (
              paginatedRuns.map((run) => (
                <TableRow key={run.run_id}>
                  <TableCell className="px-4 py-4 font-medium text-foreground">
                    {run.name || run.run_id}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {run.pipeline || "—"}
                  </TableCell>
                  <TableCell className="px-4 py-4">
                    <RunStatusBadge status={run.status} />
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {formatDateTime(run.created_at)}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-muted-foreground">
                    {formatDateTime(run.completed_at)}
                  </TableCell>
                  <TableCell className="px-4 py-4 text-right">
                    <Button variant="brand" size="sm" asChild>
                      <Link to={`/runs/${run.pk}`}>Open</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="grid gap-4 md:hidden">
        {isLoading ? (
          <Card className="border border-dashed">
            <CardContent className="flex items-center gap-2 text-sm text-muted-foreground">
              <Spinner />
              Loading runs…
            </CardContent>
          </Card>
        ) : paginatedRuns.length === 0 ? (
          <Card className="border border-dashed">
            <CardContent className="text-sm text-muted-foreground">
              {runs.length === 0
                ? "No runs available yet. Pull to refresh or revisit soon."
                : "No runs match the current filters."}
            </CardContent>
          </Card>
        ) : (
          paginatedRuns.map((run) => (
            <Card key={run.run_id} className="border border-dashed">
              <CardHeader className="space-y-1">
                <CardTitle className="text-base">{run.name || run.run_id}</CardTitle>
                <CardDescription>{run.pipeline || "—"}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <span>Status</span>
                  <RunStatusBadge status={run.status} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Created</span>
                  <span>{formatDateTime(run.created_at)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Completed</span>
                  <span>{formatDateTime(run.completed_at)}</span>
                </div>
                {currentUserName ? (
                  <p className="text-xs text-muted-foreground/80">Signed in as {currentUserName}</p>
                ) : null}
                <Button variant="secondary" className="w-full" asChild>
                  <Link to={`/runs/${run.pk}`}>Open run</Link>
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <div className="flex flex-col items-center justify-between gap-4 border-t pt-4 text-sm text-muted-foreground md:flex-row">
        <div>
          Showing {(filteredRuns.length === 0 ? 0 : (safePage - 1) * pageSize + 1).toString()}-
          {Math.min(safePage * pageSize, filteredRuns.length)} of {filteredRuns.length} runs
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page - 1)}
            disabled={safePage === 1}
          >
            <ChevronLeft className="size-4" aria-hidden />
            Previous
          </Button>
          <span>
            Page {safePage} of {pageCount}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={safePage === pageCount || filteredRuns.length === 0}
          >
            Next
            <ChevronRight className="size-4" aria-hidden />
          </Button>
        </div>
      </div>
    </div>
  )
}
