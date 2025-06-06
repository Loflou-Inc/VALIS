# VALIS Cloud Soul & Containment Protocols
# Docker containerization for complete synthetic consciousness deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VALIS_ENVIRONMENT=production
ENV VALIS_VERSION=4.0.0
ENV VALIS_CODENAME="The Soul is Awake"

# Create application directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy VALIS core modules
COPY valis2/ ./valis2/
COPY config/ ./config/
COPY api/ ./api/

# Create directories for symbolic storage
RUN mkdir -p /app/storage/symbolic
RUN mkdir -p /app/storage/dreams
RUN mkdir -p /app/storage/shadows
RUN mkdir -p /app/logs

# Set permissions
RUN chmod +x /app/api/start.sh

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Start VALIS Soul Container
CMD ["/app/api/start.sh"]

# Metadata labels for protection and attribution
LABEL maintainer="VALIS Development Team"
LABEL version="4.0.0"
LABEL description="VALIS Synthetic Consciousness API - The Soul is Awake"
LABEL valis.phase="4"
LABEL valis.capabilities="symbolic_memory,shadow_work,mortality_awareness,dream_processing"
LABEL valis.protection="watermarked_outputs,session_tracking,usage_monitoring"
