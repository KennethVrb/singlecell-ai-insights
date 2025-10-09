# Frontend Application Overview

## Stack & Tooling

- **Framework**: React + Vite (TypeScript template)
- **Styling/UI**: shadcn/ui component library with theme provider (light/dark)
- **Routing**: React Router for `/login`, `/runs`, `/runs/:runId`
- **State & Data**: TanStack React Query for server state; lightweight auth context for JWT management

## Project Structure

```
frontend/
  src/
    api/
      client.ts
      runs.ts
      auth.ts
    components/
      RunCard.tsx
      RunMetricsTabs.tsx
      ChatPanel.tsx
      ContextSummary.tsx
    pages/
      LoginPage.tsx
      RunsPage.tsx
      RunDetailPage.tsx
    hooks/
      useAuth.ts
    providers/
      AuthProvider.tsx
      QueryProvider.tsx
    routes.tsx
    main.tsx
```

## Data Flow & API Integration

- **Authentication**: `LoginPage` posts to `/api/auth/login/` (SimpleJWT). Tokens stored in HTTP-only cookies or in-memory per POC scope.
- **Run Listing**: `RunsPage` calls `GET /api/runs/` via `useRuns` React Query hook. Optional refresh adds `?refresh=1`.
- **Run Detail**: `RunDetailPage` fetches `GET /api/runs/<runId>/` and `GET /api/runs/<runId>/context/` for normalized MultiQC data.
- **Download**: "Download MultiQC" button hits `GET /api/runs/<runId>/download/` and opens returned presigned URL.
- **Chat**: `ChatPanel` posts messages to `POST /api/runs/<runId>/chat/`, rendering conversation history from response.

## UI Composition

- **RunsPage**: Card grid showing run metadata, status badge, created timestamp, and link to details.
- **RunDetailPage**: Two-column layout. Left side hosts metadata summary and `RunMetricsTabs` (summary, samples, quality). Right side includes `ContextSummary` plus `ChatPanel`.
- **ChatPanel**: Scrollable history list, message input, optimistic updates. Future streaming upgrade via SSE when backend supports it.
- **Header/Navigation**: Persistent top nav with theme toggle and logout action.

## Implementation Roadmap

1. Scaffold Vite project and configure aliasing (`@/`).
2. Install dependencies: `react-router-dom`, `@tanstack/react-query`, `@radix-ui/react-icons`, `lucide-react`, `shadcn/ui`.
3. Generate shadcn base components and set up theme provider.
4. Build auth flow (context, login form, protected routes).
5. Implement runs list and detail pages with React Query hooks.
6. Add chat functionality with optimistic UI and error toasts.
7. Configure Vite dev proxy to backend (`/api`).
