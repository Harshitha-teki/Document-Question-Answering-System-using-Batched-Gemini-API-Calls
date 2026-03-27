# Use a slim Python image for a smaller footprint
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
# 1. curl: Required for the healthcheck in docker-compose
# 2. libmagic1: Often required for file type detection (optional but recommended)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Expose the port defined in your .env (defaulting to 8000 here)
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
# --host 0.0.0.0 is mandatory for Docker networking
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]