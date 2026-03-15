# app/Dockerfile
FROM python:3.11-slim

# Flat WORKDIR
WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the current WORKDIR (/app)
COPY app/ .

# Ensure /app is in the path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Command: Run main.py directly
# This gives us the clearest logs and avoids any hidden ADK runner issues
CMD ["python", "main.py"]
