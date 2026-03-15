# app/Dockerfile
FROM python:3.11-slim

# WORKDIR at /app for a flat structure inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the app directory directly into /app
COPY app/ .

# Ensure the current directory is in the Python path
ENV PYTHONPATH=/app

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent using the official ADK runner
# We point it to the app object in main.py
CMD ["python", "-m", "google.adk.runner", "--app", "main:app"]
