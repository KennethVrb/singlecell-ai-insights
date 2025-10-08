# Frontend Next Steps

## Immediate Tasks

- [x] **Scaffold routing structure**: Add `src/routes.tsx` and empty page components `pages/LoginPage.tsx`, `pages/RunsPage.tsx`, `pages/RunDetailPage.tsx`.
- [x] **Set up global providers**: Create `providers/AuthProvider.tsx` and `providers/QueryProvider.tsx`, then wrap them around `RouterProvider` in `src/main.tsx`.
- [x] **Seed API layer**: Introduce `api/client.ts`, `api/auth.ts`, and `api/runs.ts` with placeholder fetch helpers pointing at `/api/...` endpoints.
- [ ] **Auth workflow skeleton**: Implement a basic `LoginPage` form that calls the auth client, stores tokens via context, and redirects to `/runs`.
- [ ] **Shared layout**: Draft a shadcn-based `AppShell` (header + sidebar) to keep typography and spacing consistent across pages.

## Follow-Up Considerations

- **React Query integration**: Define `useRuns`, `useRun`, `useRunContext`, and `useRunChat` hooks backed by the API layer once endpoints are ready.
- **Protected route handling**: Add route guards that check authentication state before rendering data pages.
- **Styling tokens**: Expand shared theme utilities (`lib/utils.ts`, `components/ui`) so future components have consistent modifiers.
- **Dev tooling**: Add npm scripts for `lint`, `format`, and optionally `test`, ensuring they match pre-commit hooks.
