# app/Dockerfile
FROM python:3.11-slim

# WORKDIR at root so that 'app' is a package
WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Pre-download the Cross-Encoder model to avoid timeout at startup
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Copy the entire app directory into /app
COPY app /app

# Ensure /app is in the Python path
ENV PYTHONPATH=/

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent
# Using the official runner and specifying the 'app' module
CMD ["python", "-m", "google.adk.runner", "--app", "app"]
