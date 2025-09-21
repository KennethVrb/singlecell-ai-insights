# SingleCell AI Insights

This repository contains a proof-of-concept platform that explores how a conversational
assistant can help researchers interrogate curated nf-core/singlecell reports.

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
