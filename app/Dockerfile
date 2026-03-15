# app/Dockerfile
FROM python:3.11-slim

# WORKDIR at root so that 'app' is a package
WORKDIR /

# Set environment variables for model caching
ENV SENTENCE_TRANSFORMERS_HOME=/app/model_cache
ENV TORCH_HOME=/app/model_cache
ENV PYTHONPATH=/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Pre-download the Cross-Encoder model to the specific cache directory
RUN mkdir -p /app/model_cache && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Copy the entire app directory into /app
COPY app /app

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent
# Using the custom main.py for maximum logging and control
CMD ["python", "-m", "app.main"]
