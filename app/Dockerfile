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

# Command: Use uvicorn directly to ensure the port is correctly handled and the application starts reliably.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
