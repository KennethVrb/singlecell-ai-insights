# Single-cell AI Insights Backend

Backend service built with Django and Django REST Framework to surface metadata from AWS HealthOmics pipelines. The project persists run details locally so they can be revisited quickly after the initial fetch from AWS.

## Requirements
- Python 3.10+
- pip / virtualenv tooling of your choice
- AWS credentials with permission to call the HealthOmics APIs
- SQLite works out of the box; you can point Django at another database if preferred

## Quick Start
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/singlecell_ai_insights/requirements.txt
   ```
   For local tooling (shell plus extras) you can also install:
   ```bash
   pip install -r backend/dev-requirements.txt
   ```
3. Copy the example environment file and adjust it for your setup:
   ```bash
   cp backend/singlecell_ai_insights/.env-example backend/singlecell_ai_insights/.env
   ```
   | Variable | Purpose |
   | --- | --- |
   | `DJANGO_SECRET_KEY` | Unique secret for Django cryptographic signing. |
   | `DJANGO_DEBUG` | Enables Django debug mode when set to `True`. |
   | `DJANGO_ALLOWED_HOSTS` | Comma-delimited hostnames the server will accept. |
   | `DJANGO_CORS_ALLOWED_ORIGINS` | Origins allowed to access the API via browsers. |
4. Apply migrations:
   ```bash
   python backend/manage.py migrate
   ```
5. Create an initial user (optional but handy for admin/browsable API access):
   ```bash
   python backend/manage.py createsuperuser
   ```

`boto3` automatically discovers AWS credentials from your environment (environment variables, shared credentials file, instance profile, and so on).

## Running Locally
Start the development server with:
```bash
python backend/manage.py runserver
```

The app serves the DRF browsable interface by default. Use the login link exposed through `rest_framework.urls` or obtain JWT tokens via the SimpleJWT endpoints listed in `backend/singlecell_ai_insights/urls.py` to access authenticated resources.

## Testing
Automated tests live under `backend/singlecell_ai_insights/tests/`. Run them with:
```bash
pytest backend/singlecell_ai_insights/tests
```
or using Django’s runner:
```bash
python backend/manage.py test
```

## Project Structure Highlights
- `backend/singlecell_ai_insights/models/run.py` – persistence for cached HealthOmics runs.
- `backend/singlecell_ai_insights/aws/` – integrations with AWS services (e.g., HealthOmics clients).
- `backend/singlecell_ai_insights/api/` – DRF views, serializers, and URL configuration.
- `docs/` – additional design notes and architecture references.
