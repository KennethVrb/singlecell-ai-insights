# Next Steps Roadmap

## Backend (`backend/`)
- **Bedrock knowledge base integration**
  - [ ] Provision an AWS Bedrock Knowledge Base, configure embeddings model, and connect it to curated nf-core outputs stored in S3.
  - [ ] Build an ingestion job (serverless batch or management command) to normalize HTML/CSV/PNG artifacts, push metadata, and sync documents into the knowledge base.
  - [ ] Replace `answer_chat_query()` placeholder in `backend/scrna_ai_insights/services.py` with Bedrock KB retrieval + LLM call, including guardrails for empty hits and latency logging.
- **API contract hardening**
  - [ ] Extend `schemas.py` to surface citation metadata returned by Bedrock (e.g., chunk IDs, S3 paths) and update tests under `backend/scrna_ai_insights/tests/`.
  - [ ] Add input validation and rate-limiting hooks (e.g., Django middleware) before exposing public endpoints.
- **Observability & resilience**
  - [ ] Instrument structured logging around Bedrock calls and retrieval scoring.
  - [ ] Add retries/backoff for transient AWS errors and surface user-friendly messages.

## Frontend (`frontend/`)
- **Chat experience polish**
  - [ ] Replace placeholder copy in `ChatPanel` with streaming or loading indicators tied to real backend latency.
  - [ ] Display citations with source summaries (e.g., artifact type, section title) once backend returns richer metadata.
- **Report discovery**
  - [ ] Add filtering/search to the `ReportSelector` when catalog grows beyond a handful of items.
  - [ ] Implement contextual previews in `ContextPanel` (render HTML snapshot, chart thumbnails) using signed URLs from the backend.
- **State management & error handling**
  - [ ] Centralize toast/error surface for network issues and disambiguate between 4xx vs 5xx responses.
  - [ ] Persist conversation history in local storage so refreshes do not drop context.

## Data preparation pipeline
- **Artifact normalization**
  - [ ] Create scripts to convert nf-core outputs into text chunks, table summaries, and image descriptors prior to Bedrock ingestion.
  - [ ] Store derived metadata (e.g., cell cluster labels) in DynamoDB or a lightweight JSON catalog for fast lookup.

## Infrastructure & DevOps
- **Environment provisioning**
  - [ ] Draft IaC (Terraform or CDK) for API Gateway, Lambda, Bedrock KB, S3 buckets, and DynamoDB tables.
  - [ ] Configure CI to run backend tests (`python backend/manage.py test`) and frontend builds (`npm run build`) on each push.
- **Deployment workflow**
  - [ ] Package Django app for Lambda (container image or zip) with secure configuration for Bedrock + AWS Secrets Manager.
  - [ ] Set up frontend deployment to S3 + CloudFront with environment-specific API base URLs.

## Testing & QA
- **Automated testing**
  - [ ] Expand backend tests to cover failure paths (missing citations, Bedrock timeouts) and contract fixtures.
  - [ ] Add React Testing Library coverage for chat flows, artifact rendering, and error states.
- **Manual validation**
  - [ ] Define QA checklist covering typical scientist workflows (QC questions, cluster comparisons, artifact exploration).

## Documentation & Enablement
- **Operational docs**
  - [ ] Update `README.md` with Bedrock Knowledge Base setup prerequisites, IAM policies, and environment variable requirements.
  - [ ] Provide runbooks for data ingestion, vector refresh, and troubleshooting common errors.
- **User guidance**
  - [ ] Draft onboarding guide explaining how scientists select reports, interpret citations, and request new datasets.
