# UI Branding Enhancements

- [ ] **Define brand palette**: Extend `tailwind.config.ts` with brand colors (e.g., `brand`, `status.success`, `status.warning`, `status.error`) for consistent use across components.
- [x] **Status badges**: Update status chips in `frontend/src/pages/RunsPage.tsx` to use brand-color utilities (`bg-emerald-100 text-emerald-700`, `bg-amber-100 text-amber-700`, etc.) and add icon indicators.
- [ ] **Card hero accents**: Introduce a `.card-accent` utility in `frontend/src/index.css` (gradient background, subtle border glow) and apply to hero cards like `Run overview` and `Chat activity`.
- [ ] **Primary button variant**: Extend `frontend/src/components/ui/button.tsx` with a `brand` variant leveraging the new palette; use it for call-to-action buttons (e.g., `Open`, `Download`, chat prompts).
- [x] **Navigation header styling**: Add gradient or accent border to the header in `frontend/src/components/MainLayout.tsx` for a distinctive top bar.
- [ ] **Chat panel theme**: Customize the chat card in `frontend/src/pages/RunDetailPage.tsx` with a darker/tinted background, left-edge accent, and typography tweaks to mimic a chat surface.
- [ ] **Iconography**: Incorporate `lucide-react` icons into card headers (e.g., `Activity`, `BarChart3`) and adjust typography (`uppercase`, `tracking-wide`) for section labels.
- [ ] **Background sections**: Add optional background panels (e.g., `bg-slate-950/40 ring-1 ring-white/10`) for runs list and metrics sections to break up the layout.
- [ ] **Global typography settings**: Update Tailwind base styles (via `@layer base` in `frontend/src/index.css`) to fine-tune font weights, letter spacing, and heading hierarchy.
