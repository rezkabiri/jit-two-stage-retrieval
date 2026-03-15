# app/Dockerfile
FROM python:3.11-slim

WORKDIR /

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory
COPY app/ /app/

# Ensure the root is in the path
ENV PYTHONPATH=/

# Expose port
EXPOSE 8080

# Command: Run as a module to ensure absolute imports work
CMD ["python", "-m", "app.main"]
