# Next Steps Roadmap

## Backend (`backend/`)
- **HTML normalization**
  - [ ] Build an AWS Lambda (or Django management command) that fetches raw report HTML from S3, strips boilerplate, and writes normalized sections back to S3 as structured JSON.
  - [ ] Add a lightweight trigger in Django to re-run normalization when a report is added or updated.
- **Bedrock integration**
  - [ ] Replace `answer_chat_query()` with logic that loads normalized text, selects relevant sections (keyword or simple scoring), and calls an AWS Bedrock text model with a grounded prompt.
  - [ ] Capture request/response metadata, handle empty context gracefully, and surface friendly errors to the client.
- **API contract hardening**
  - [ ] Update `schemas.py` to expose optional section titles/source URLs alongside answers.
  - [ ] Extend tests in `backend/scrna_ai_insights/tests/` to cover success, empty-context, and Bedrock failure paths.

## Frontend (`frontend/`)
- **Chat experience polish**
  - [ ] Show a loading indicator while Bedrock responses are pending and disable the send button during inference.
  - [ ] Render returned section titles or citations inline when available.
- **Context panel improvements**
  - [ ] Display normalized HTML sections in `ContextPanel` with expand/collapse behavior.
  - [ ] Provide fallback messaging when normalized content cannot be retrieved.

## Data preparation
- **Report onboarding**
  - [ ] Create a simple script to upload a sample nf-core HTML report to S3 and register its metadata (report ID, normalized text key).
  - [ ] Document normalization assumptions (max size, ignored sections) for future data sources.

## Infrastructure & DevOps
- **Serverless plumbing**
  - [ ] Provision S3 bucket, normalization Lambda, IAM roles, and required environment variables via lightweight IaC (Terraform or CDK).
  - [ ] Configure API Gateway + Lambda (or container) deployment for the Django service with access to Bedrock and S3.
- **CI basics**
  - [ ] Add continuous integration to run `python backend/manage.py test` and `npm run build` on each push.

## Testing & QA
- **Automated checks**
  - [ ] Add unit tests for HTML normalization logic (section extraction, cleaning, chunking).
  - [ ] Add React Testing Library coverage for chat flow, loading states, and error surfaces.
- **Manual validation**
  - [ ] Draft a checklist ensuring at least one report answers representative questions and handles failure cases (Bedrock errors, missing normalized text).

## Documentation & Enablement
- **Operational docs**
  - [ ] Update `README.md` with Bedrock credential requirements, Lambda deployment steps, and normalization workflow.
  - [ ] Provide a quickstart for running normalization locally and invoking the backend chat endpoint.
- **User guidance**
  - [ ] Capture example prompts and screenshots showing the assistant summarizing the sample report.
