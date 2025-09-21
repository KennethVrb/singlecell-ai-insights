# SingleCell AI Insights

This repository contains a proof-of-concept platform that explores how a conversational
assistant can help researchers interrogate curated nf-core/singlecell reports.

The codebase is split into two major pieces:

- A minimal Django + Django Ninja backend that exposes the API contract outlined in
  [`SPEC.md`](./SPEC.md).
- A Vite-powered React frontend that consumes the backend and offers report browsing,
  artifact exploration, and a conversational assistant experience.

The sections below walk through the expected local development workflow for both halves
of the stack.

## Backend (Django + Django Ninja)

A lightweight Django project powers the API surface that the frontend will consume,
all contained within a single Django application package named `scrna_ai_insights`
under `backend/` to keep things straightforward. The API is implemented with
[Django Ninja](https://django-ninja.dev/) and currently
provides scaffolded endpoints that mirror the high-level contract described in the
project specification.

### Getting started

1. Create and activate a virtual environment (optional but recommended).
2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Apply the default Django migrations:

   ```bash
   python backend/manage.py migrate
   ```

4. Start the development server:

   ```bash
   python backend/manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`. Example endpoints include:

- `GET /api/reports`
- `GET /api/reports/{report_id}/artifacts`
- `POST /api/chat/query`

These endpoints currently return static placeholder data to illustrate the wire format
for future integrations with the retrieval layer, vector store, and AWS Bedrock model
invocations outlined in the specification.

## Frontend (React + Vite + TypeScript)

The frontend lives in the `frontend/` directory and is scaffolded with Vite and React
Query. It is responsible for rendering the report selector, chat panel, and contextual
artifact browser that orchestrate requests against the Django API described above.

### Getting started

1. Install the JavaScript dependencies (Node.js 18+ recommended):

   ```bash
   cd frontend
   npm install
   ```

2. Start the Vite development server:

   ```bash
   npm run dev -- --host
   ```

   The `--host` flag allows external connections (e.g., Docker port forwarding). By
   default, the app will be served at `http://127.0.0.1:5173`.

3. Ensure the Django API is running (see the backend instructions above). The frontend
   expects the API to be reachable at `http://127.0.0.1:8000/api`. If you need to target
   a different origin, update the `API_BASE_URL` constant in `frontend/src/api.ts`.

During development Vite automatically hot-reloads the UI whenever files under
`frontend/src/` change.

## Running the full stack

To exercise the full experience locally:

1. Start the Django API server on port `8000`.
2. Launch the Vite dev server on port `5173`.
3. Navigate to the frontend in your browser. Selecting a report will populate the chat
   and context panes using the mock payloads provided by the backend.

Because the backend currently returns static data, the chat interface will always
respond with the same placeholder conversation. This scaffolding is intentionally
lightweight so that the retrieval and LLM integration layers described in the spec can
be swapped in with minimal plumbing changes.
