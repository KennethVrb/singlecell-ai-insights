---
trigger: always_on
---

# Backend Application Overview

## Stack & Tooling

- **Framework**: Django 4.2 (`backend/`)
- **API Layer**: Django REST Framework for viewsets, serializers, and API views
- **Auth**: `djangorestframework-simplejwt` with cookie-based JWT storage
- **Background Integrations**: AWS HealthOmics via boto3, Bedrock (chat + embeddings), FAISS vector store (LangChain community)
- **Testing**: pytest-style tests under `singlecell_ai_insights/tests/`
- **Configuration**: Environment-driven settings (`backend/.env`, `singlecell_ai_insights/settings.py`)

## Project Structure

```
backend/
  manage.py
  requirements.txt
  singlecell_ai_insights/
    __init__.py
    settings.py             # Django settings incl. AWS + JWT config
    urls.py                 # API routes (`/api/...`)
    authentication.py       # Custom auth helpers (cookie JWT)
    models/
      run.py                # Run metadata + MultiQC helpers
      user.py               # Simple user proxy
    api/
      runs/
        serializers.py      # `RunSerializer`, `RunSummarySerializer`
        views.py            # `RunViewSet` with HealthOmics refresh + MultiQC presign
      auth/
        serializers.py      # Custom SimpleJWT serializers (cookie-aware)
        views.py            # Login, refresh, logout, me endpoints
      agent/
        serializers.py
        views.py            # `RunAgentChatView` bridge to agent service
      health.py             # `/api/health/` endpoint
    aws/
      healthomics.py        # HealthOmics client normalization utilities
    services/
      agent.py              # LangGraph workflow orchestrating chat responses
    migrations/
    tests/
      test_run_chat.py      # Agent chat API tests
```

## Core Concepts

- **Run model**: `Run` (`models/run.py`) stores AWS HealthOmics run metadata, MultiQC output locations, and normalized context JSON. It exposes helpers like `get_multiqc_report_url()` to generate presigned S3 links.
- **HealthOmics sync**: `api/runs/views.py` checks for `?refresh=true` or empty DB and then calls `aws/healthomics.list_runs()` to upsert runs in the database.
- **MultiQC artifacts**: `RunViewSet.multiqc_report` uses `Run.get_multiqc_report_url()` for download links. `services/agent.py` fetches `multiqc_data.json`, builds in-memory FAISS index, and returns answers/artifacts.
- **Agent graph**: `services/agent.py` composes LangGraph nodes (`load_multiqc`, `ensure_index`, `lookup_*`, `rag`, `make_table`, `plot_metric`, `synthesize`) to answer questions, potentially uploading CSV/PNG artifacts back to S3 and returning presigned URLs.
- **Authentication**: `api/auth/views.py` wraps SimpleJWT views to set/clear cookies (`AUTH_COOKIE`, `AUTH_REFRESH_COOKIE`). `LogoutView` blacklists refresh tokens when present.
- **Routing**: `urls.py` binds REST endpoints under `/api/`, including `/api/runs/<pk>/chat/` for the agent, `/api/auth/*` for session handling, and `/api/health/`.

## External Dependencies & Credentials

- **AWS Clients**: Configured via environment variables (`AWS_REGION`, `REPORTS_BUCKET`, `ARTIFACT_BUCKET`, `BEDROCK_MODEL_ID`, `BEDROCK_EMBED_MODEL_ID`). `settings.py` wires boto3 clients (`AWS_S3_CLIENT`, `AWS_HEALTHOMICS_CLIENT`).
- **LangChain / Bedrock**: `services/agent.py` instantiates `ChatBedrock` + `BedrockEmbeddings` once at import time; ensure credentials allow access to the selected models.
- **S3 Artifacts**: `_put_s3_bytes_and_presign()` uploads generated CSV/PNG files under `<run_id>/artifacts/` in `ARTIFACT_BUCKET`.

## Development Workflow

- Copy `backend/.env-example` → `.env` and populate AWS + JWT settings (including cookie domains when required).
- Install dependencies via `pip install -r requirements.txt` (or `pip install -r dev-requirements.txt` for tooling extras).
- Run migrations: `python manage.py migrate`.
- Start dev server: `python manage.py runserver`. HealthOmics sync requires AWS credentials with `omics:*` and `s3:*` permissions.
- Execute tests: `pytest` or `python manage.py test` (see `tests/`).

## Windsurf Context Notes

- Treat this document as the authoritative backend rules reference when crafting Windsurf automation or assistance.
- When editing backend code, preserve DRF patterns, keep functions small (KISS/YAGNI), and avoid introducing Python typing annotations per project conventions.
