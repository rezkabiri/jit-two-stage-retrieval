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
# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

# Cloud Run uses 8080 by default
EXPOSE 8080

# Command: Run the app using the python module runner. 
# This ensures the if __name__ == "__main__": block is executed.
CMD ["python3", "-m", "app.main"]
