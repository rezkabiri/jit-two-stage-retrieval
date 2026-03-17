# app/Dockerfile
FROM python:3.11-slim

WORKDIR /

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repo's app directory to /app
COPY app/ /app/

# Ensure the parent directory is in the path so "import app.main" works
ENV PYTHONPATH=/

# Expose port (metadata only)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Command: Use uvicorn directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
