# Retail & CPG Customer Service Chatbot - Dockerfile
# ===================================================
# 
# This Dockerfile creates a production-ready container for the chatbot application.
# It includes all necessary dependencies, security best practices, and optimization
# for cloud deployment.

# Use Python 3.11 slim image for smaller size and better security
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Multi-stage build for production optimization
# Uncomment the following section for production builds

# FROM python:3.11-slim as production

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1

# WORKDIR /app

# # Install only runtime dependencies
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         curl \
#     && rm -rf /var/lib/apt/lists/*

# # Create non-root user
# RUN groupadd -r appuser && useradd -r -g appuser appuser

# # Copy only the necessary files from build stage
# COPY --from=0 /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=0 /usr/local/bin /usr/local/bin
# COPY --from=0 /app /app

# # Set permissions
# RUN chown -R appuser:appuser /app

# USER appuser

# EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
