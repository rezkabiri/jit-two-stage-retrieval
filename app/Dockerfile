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

# Pre-download the Cross-Encoder model to avoid timeout at startup
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Copy agent code
COPY . .

# Ensure the app is in the Python path
ENV PYTHONPATH=/app

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent
# Note: Using python -m to ensure the 'app' package is in the path
CMD ["python", "-m", "app.main"]
