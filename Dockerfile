# GitHub Governance Factory - Production Docker Image
# Multi-stage build for optimized container size

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r governance && useradd -r -g governance governance

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/governance/.local

# Copy application code
COPY src/ src/
COPY cli.py .
COPY .env.example .env

# Create necessary directories
RUN mkdir -p logs backups \
    && chown -R governance:governance /app

# Set environment variables
ENV PATH=/home/governance/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER governance

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health || exit 1

# Expose ports for microservices
EXPOSE 8000 8001 8002 8003

# Default command - start all microservices
CMD ["python", "cli.py", "serve", "--service", "all"]
