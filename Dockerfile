# Stage 1: Build Environment
FROM python:3.11-slim as builder

WORKDIR /app

# Install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Copy files from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# Cloud Run expects the service to listen on the port defined by the PORT environment variable (default 8080)
ENV PORT 8080

# Command to run your application using Uvicorn
# The format is uvicorn [module_name]:[app_instance_name] --host 0.0.0.0 --port $PORT
CMD exec uvicorn main_api:app --host 0.0.0.0 --port $PORT
