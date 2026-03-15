# app/Dockerfile
FROM python:3.11-slim

WORKDIR /

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory
COPY app/ /app/

# Ensure the root is in the path
ENV PYTHONPATH=/

# Cloud Run uses 8080 by default
EXPOSE 8080

# Command: Run uvicorn directly
# This is the most reliable way to ensure port 8080 is listening
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]
