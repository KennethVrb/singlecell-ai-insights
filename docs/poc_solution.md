# HealthOmics MultiQC Chatbot POC Plan

## Goals
- Replace the existing CLI-only MultiQC chatbot with a simple full-stack proof of concept.
- Showcase how HealthOmics runs stored in an AWS account can be inspected through a web UI.
- Allow scientists to review metrics, download MultiQC reports, and chat with a Claude on Bedrock agent using the run-specific context pulled from S3.
- Keep the solution lightweight: React + Vite + shadcn/ui on the frontend, Django + Django REST Framework on the backend.

## High-Level Architecture
```text
┌─────────────────────┐          ┌───────────────────────────────┐
│ React (Vite) client │◀────────▶│ Django REST API (DRF)         │
│ - run list view     │   HTTPS  │ - Run metadata endpoints      │
│ - run detail + chat │          │ - MultiQC download proxy      │
└─────────────────────┘          │ - Bedrock chat orchestration  │
                                 │ - AWS Auth (SigV4) helpers     │
                                 └───────────────────────────────┘
                                                  │
                                                  ▼
                                      ┌─────────────────────┐
                                      │ AWS services        │
                                      │ - HealthOmics runs  │
                                      │ - S3 report bucket  │
                                      │ - Bedrock runtime   │
                                      └─────────────────────┘
```

### Data Flow Summary
1. Frontend authenticates the user (for the POC, issue short-lived JSON Web Tokens (JWT) via DRF SimpleJWT and store them in HTTP-only cookies or in-memory state to keep the flow lightweight yet secure).
2. Frontend calls `/api/runs/` to list HealthOmics runs. The backend retrieves run metadata through the AWS HealthOmics API using configured AWS credentials.
3. Selecting a run calls `/api/runs/<id>/` for metrics and `/api/runs/<id>/download/` for a presigned S3 URL to the MultiQC report.
4. When the user opens the chat panel, the frontend fetches `/api/runs/<id>/context/` (normalized MultiQC JSON). The backend downloads the run's report from S3, runs the existing normalizer, and persists the normalized context in the `Run` record for reuse.
5. Chat requests POST to `/api/runs/<id>/chat/` with the user message. The backend reuses the existing `ClaudeBedrockChat` wrapper to call Bedrock while persisting the conversation history to the database.
6. Responses stream back to the frontend (use Server-Sent Events or simple JSON for POC).

## Backend (Django + DRF)

### Project Setup
- Create a Django project named `singlecell_ai_insights` that also acts as the single app module (keep `INSTALLED_APPS = ["singlecell_ai_insights", "rest_framework", ...]`).
- Immediately scaffold a custom user model: add `class User(AbstractUser)` in `singlecell_ai_insights/models.py`, update `AUTH_USER_MODEL = "singlecell_ai_insights.User"`, and create an initial migration before building additional features.
- Install Django REST Framework and `boto3` (already required).
- Configure AWS credentials via environment variables or IAM role.

### Models (POC-friendly)
For the proof of concept we can keep the database minimal while still storing critical context:
- `Run` table to cache metadata fetched from AWS and persist normalized context. Suggested fields: `run_id`, `name`, `status`, `pipeline`, `created_at`, `updated_at`, `s3_report_key`, `metadata` JSON, `normalized_context` JSON (nullable until first normalization run).
- `ChatSession` keyed by user and run to anchor each conversation (`id`, `user`, `run`, `created_at`, `updated_at`).
- `ChatMessage` linked to a `ChatSession` for storing ordered history (`session`, `role`, `content`, `created_at`).

### Serializers & Views
- Keep all API logic inside the single `singlecell_ai_insights` Django app (e.g., submodules such as `singlecell_ai_insights.api.serializers` and `singlecell_ai_insights.api.views`).
- Serializers:
  - `RunSerializer` returning a subset of HealthOmics run metadata.
  - `RunMetricsSerializer` using the normalized MultiQC payload (`summary`, `samples`, `quality_summary`).
- Views (class-based with DRF):
  - `RunListView` (`GET /api/runs/`): call `list_runs` helper that wraps `boto3.client("omics").list_runs()`.
  - `RunDetailView` (`GET /api/runs/<id>/`): call `get_run` helper for details plus normalized metrics.
  - `RunDownloadView` (`GET /api/runs/<id>/download/`): return a presigned URL for MultiQC report stored in S3 via `boto3.client("s3").generate_presigned_url`.
  - `RunContextView` (`GET /api/runs/<id>/context/`): returns normalized MultiQC JSON; populates `Run.normalized_context` when missing and reuses the stored value on subsequent requests.
  - `RunChatView` (`POST /api/runs/<id>/chat/`):
    - Accepts `{"message": "..."}`.
    - Loads or creates a `ChatSession` for the current user + run.
    - Initializes `ClaudeBedrockChat` with `set_context(context_text=run.normalized_context)`.
    - Persists both the user message and the assistant reply in `ChatMessage` rows tied to the session.
    - Returns `{ "reply": "...", "history": [...] }` built from the stored messages.

### Reusing Existing Code
- Move `src/chat/bedrock.py` into `singlecell_ai_insights/bedrock.py`. Adapt to use Django settings for defaults.
- Move `src/tools/normalizer.py` into `singlecell_ai_insights/normalizer.py`. Expose helper `normalize_bytes(data: bytes) -> dict` to avoid temp files.
- Create `singlecell_ai_insights/s3_reports.py` with functions to download MultiQC `multiqc_data.json` from S3; normalized results get persisted to the `Run` model rather than a transient cache.

### S3 + HealthOmics integration
- Configuration options in `settings.py` (read from env):
  - `HEALTHOMICS_ACCOUNT_ID`, `HEALTHOMICS_REGION`.
  - `HEALTHOMICS_RUN_PREFIX` (optional filter).
  - `HEALTHOMICS_S3_BUCKET`, `HEALTHOMICS_S3_PREFIX`.
- Helpers:
  - `list_runs` -> uses `omics` client `list_runs(maxResults=20)` for POC.
  - `describe_run(run_id)` -> extracts S3 location for MultiQC report.
  - `download_multiqc(run)` -> `s3.get_object(Bucket, Key)` returning JSON bytes.
  - `get_presigned_url(run)` -> `s3.generate_presigned_url('get_object', Params={'Bucket': ..., 'Key': ...}, ExpiresIn=300)`.

### Authentication
- Issue JWT access + refresh tokens using [django-rest-framework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt). Configure cookie- or header-based transport depending on hosting requirements.
- JWT improves over basic token auth by supporting short expirations, rotation, and stateless verification. For additional defense-in-depth, store access tokens in HTTP-only cookies and rotate refresh tokens on each use.
- Provide a minimal `/api/auth/login/` endpoint that authenticates against the custom `User` model and returns JWTs; the frontend should automatically refresh access tokens when needed.

## Frontend (React + Vite + shadcn/ui)

### Project Structure
```
frontend/
  src/
    api/ (fetch wrappers)
    components/
      RunList.tsx
      RunDetail.tsx
      ChatPanel.tsx
    pages/
      RunsPage.tsx
      RunDetailPage.tsx
    lib/ui (shadcn generated components)
```

### UI Flow
1. **Runs Page**
   - Fetch `/api/runs/` on load.
   - Display list in a `Card` grid (shadcn `Card`, `Badge` for status).
   - Each item links to `/runs/:id`.

2. **Run Detail Page**
   - Fetch `/api/runs/<id>/` to display high-level metrics (use `Tabs` for summary vs samples table).
   - Provide "Download MultiQC" button hitting `/api/runs/<id>/download/` (opens presigned URL).
   - Show `ChatPanel` component with conversation view and input; on mount load context snippet from `/api/runs/<id>/context/` for quick summary display.

3. **Chat Panel**
   - Maintains conversation state (array of `{role, content}`).
   - On submit, optimistically add user message, call backend `POST /api/runs/<id>/chat/`.
   - Append assistant reply on success; handle streaming later (P OC can use simple JSON response).

4. **State Management**
   - Use React Query (TanStack Query) for data fetching & caching (optional but recommended for clarity).
   - For POC keep dependencies minimal (React Query, axios/fetch wrappers).

### Styling
- Use shadcn/ui to scaffold consistent design tokens.
- Add `ThemeProvider` (light/dark) and layout with responsive sidebar.

## Bedrock Conversation Handling
- Conversation state lives in the database: create or fetch a `ChatSession` per user+run and append `ChatMessage` rows for each exchange. This keeps history durable, auditable, and reloadable after restarts without needing a separate cache.
- `ClaudeBedrockChat` service receives previous messages (queried from `ChatMessage`) plus the run context, then calls `invoke_model` using boto3.
- Make chat temperature configurable via Django settings; default to 0.2 as in current code.

## Simplified POC Implementation Steps
1. **Backend Skeleton**
   - `django-admin startproject singlecell_ai_insights`.
   - Keep the generated `singlecell_ai_insights/` package as the single Django app; organize supporting code under subpackages such as `api/`, `services/`, and `aws/`.
     - Before creating other models, implement the custom `User` model (extending `AbstractUser`), set `AUTH_USER_MODEL`, and run the initial migration so future auth tweaks are straightforward.
      - Configure DRF, AWS credentials, lightweight caching if desired for non-critical data, and URL routing under `/api/`.
    - Install and configure DRF SimpleJWT for issuing access/refresh tokens; wire login/refresh endpoints before building other views so the frontend can authenticate immediately.

2. **Port Normalizer & Chat Code**
   - Move `normalize_multiqc` logic to `singlecell_ai_insights/normalizer.py` to operate on JSON bytes.
   - Convert CLI entry to management command for debugging (optional).

3. **Implement Endpoints**
   - `RunListView`: returns simplified run metadata.
   - `RunDetailView`: returns metadata + normalized summary (call normalizer on demand, persist to `Run.normalized_context`).
   - `RunChatView`: orchestrates conversation with Bedrock, persisting chat history to `ChatMessage`.
   - `RunDownloadView`: returns presigned URL.

4. **Frontend Setup**
   - `npm create vite@latest frontend -- --template react-ts`.
   - Install `shadcn/ui` CLI, configure base styles.
   - Implement pages & routing using `react-router-dom`.
   - Add `.env` for API base URL.

5. **Integration**
   - Serve frontend via Vite dev server; configure proxy to Django dev server.
   - For production POC, use `django-cors-headers` to allow frontend origin.

6. **Testing**
   - Backend: add unit tests for normalizer helper (reusing sample data from `data/`).
   - Frontend: simple jest/vitest snapshot or just manual QA due to time.

## Deployment Considerations (Optional for POC)
- Run Django server on EC2 or container, with AWS credentials allowing access to HealthOmics, S3, and Bedrock.
- Host frontend statically (S3 + CloudFront) pointing to API domain.
- Use AWS Cognito or IAM Identity Center for authentication in production.

## Next Steps Checklist
- [ ] Bootstrap Django project & DRF endpoints.
- [ ] Port existing normalization/chat services.
- [ ] Integrate AWS SDK calls for HealthOmics + S3.
- [ ] Scaffold React/Vite UI with shadcn components.
- [ ] Wire chat UI to backend endpoints.
- [ ] Add README section referencing this POC plan.
