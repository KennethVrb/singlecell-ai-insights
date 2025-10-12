---
trigger: always_on
---

# Frontend Application Overview

## Stack & Tooling

- **Framework**: React 19 + Vite with the TypeScript template (`frontend/`)
- **Styling/UI**: Tailwind CSS 4 with shadcn/ui primitives (see `frontend/src/components/ui/`)
- **Routing**: React Router v7 (`frontend/src/routes.tsx`) gated by `ProtectedRoute`
- **State & Data**: TanStack React Query v5 for API caching, plus custom auth/global error contexts
- **Linting & Formatting**: ESLint 9 + Prettier 3 (respect ordered imports: external → aliased `@/` → relative)

## Project Structure

```
frontend/
  src/
    api/
      client.ts           # Fetch wrapper (credentials=include, JSON helpers)
      auth.ts             # Auth endpoints (login/logout/me/refresh)
      runs.ts             # Runs list/detail/multiqc + React Query hooks
    components/
      AuthLoadingScreen.tsx
      MainLayout.tsx      # Header + layout shell for authenticated routes
      ProtectedRoute.tsx  # Auth gating before rendering layout
      RunStatusBadge.tsx  # Status → badge mapping
      RunsTable.tsx       # Primary table UI for run listings
      ui/                 # shadcn/ui components (button, card, dropdown, etc.)
    hooks/
      useRunDetail.ts     # Run detail state, MultiQC download handler
      useRunsPage.ts      # Runs table orchestration + HealthOmics sync
    lib/
      datetime.ts         # Formatting helpers
      utils.ts            # Classname helpers
    pages/
      LoginPage.tsx
      RunsPage.tsx
      RunDetailPage.tsx
    providers/
      QueryProvider.tsx
      auth/               # AuthProvider + context
      global-error/       # GlobalErrorDialogProvider + context
    assets/
      logo.svg
    main.tsx
    routes.tsx
    index.css             # Tailwind theme + tokens
```

## Application Flow & API Integration

- **API base**: `requestJSON` prepends `VITE_API_BASE_URL` (default `/api`) and injects cookies for JWT auth.
- **Authentication**: `LoginPage` calls `/api/auth/login/`; tokens stored in httpOnly cookies by backend. `AuthProvider` bootstraps session via `/api/auth/me/` and handles logout (`/api/auth/logout/`) and refresh (`/api/auth/refresh/`).
- **Runs listing**: `useRunsQuery()` fetches `/api/runs/`. `useSyncRuns()` forces refresh by calling the same endpoint with `?refresh=true`, then seeds the cache.
- **Run detail**: `useRunDetail()` reads `/api/runs/<pk>/`. MultiQC downloads invoke `/api/runs/<pk>/multiqc-report/` and open the presigned URL.
- **Future chat**: `RunDetailPage` reserves UI space for the chat surface. Once wired, requests will target `/api/runs/<pk>/chat/`.
- **Error handling**: `GlobalErrorDialogProvider` listens for dispatched `ApiError` events and surfaces modal dialogs; both `useRunsPage()` and `useRunDetail()` feed errors into it.

## Routing & Layout

- **Entry**: `main.tsx` wraps `RouterProvider` with `AuthProvider`, `QueryProvider`, and `GlobalErrorDialogProvider`.
- **Routes**: `routes.tsx` redirects `/ → /runs`. `/runs` and `/runs/:runId` are wrapped in `ProtectedRoute`, which renders `MainLayout` once authentication finishes.
- **Layout**: `MainLayout` supplies the top navigation (logo, user dropdown) and hosts routed pages within a centered container. Tailwind utilities plus shadcn/ui components enforce consistent spacing/typography.

## UI Composition Highlights

- **`RunsPage`**: Presents intro copy, HealthOmics sync CTA, and renders `RunsTable` with loading/error states.
- **`RunsTable`**: Uses shadcn table primitives to display run metadata, status badges, timestamps, and row navigation to run detail.
- **`RunDetailPage`**: Two-column layout combining metadata cards, normalized context preview, and a placeholder chat panel that becomes interactive when runs complete.
- **`RunStatusBadge`**: Maps status strings to semantic badge variants via Tailwind utility classes.
- **`AuthLoadingScreen`**: Full-screen spinner used during auth bootstrap.

## Local Development Notes

- Install dependencies with `pnpm install` (or npm/yarn aligned with `package.json`).
- Create `.env` with `VITE_API_BASE_URL` pointing at Django (e.g., `http://localhost:8000/api`).
- Run `pnpm dev` to start Vite; Tailwind 4 uses the new `@theme` inline tokens declared in `index.css`.
- Follow import order conventions: third-party, then `@/` aliases, then relative paths with blank lines between groups.

Use this document as authoritative context for Windsurf rules when editing the frontend.
