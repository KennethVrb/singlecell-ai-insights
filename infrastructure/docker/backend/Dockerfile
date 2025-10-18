FROM python:3.12-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir psycopg2-binary gunicorn

# Create non-root user
RUN useradd -m -u 1000 django && \
    mkdir -p /app && \
    chown -R django:django /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=django:django backend/ /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=singlecell_ai_insights.settings \
    MPLBACKEND=Agg

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Run gunicorn
CMD ["gunicorn", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "2", \
    "--threads", "4", \
    "--worker-class", "gthread", \
    "--worker-tmp-dir", "/dev/shm", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "singlecell_ai_insights.wsgi:application"]
