# app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent (assuming ADK uses a standard entry point)
CMD ["python", "-m", "google.adk.runner", "--port", "8080"]
