# app/Dockerfile
FROM python:3.11-slim

WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire app directory into /app
COPY app /app

# Ensure /app is in the Python path
ENV PYTHONPATH=/

# Expose the port (ADK defaults to 8080)
EXPOSE 8080

# Command to run the agent
CMD ["python", "-m", "app.main"]
