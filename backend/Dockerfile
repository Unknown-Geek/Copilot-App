# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Download NLTK data
RUN python -m nltk.downloader vader_lexicon punkt averaged_perceptron_tagger

# Copy application code
COPY . .

# Create directory for exports
RUN mkdir -p /app/exports

# Expose port
EXPOSE 5001

# Health check (uses PORT env var or defaults to 5001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests, os; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"5001\")}/api/config')" || exit 1

# Run with gunicorn (bind to PORT env var or default to 5001)
CMD gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 2 --timeout 120 server:app
