# 🚀 VALIS DEPLOYMENT DOCKERFILE
# Doc Brown's Temporal Disaster Prevention Container
# Multi-Stage Build with Security & Performance Optimization

# Stage 1: Frontend Build Environment
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install dependencies with security audit
RUN npm ci --only=production && \
    npm audit --audit-level=moderate

# Copy frontend source
COPY frontend/ ./

# Build optimized production frontend
RUN npm run build

# Stage 2: Python Backend Environment  
FROM python:3.11-slim AS backend-builder

# Set working directory for backend
WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Production Runtime Environment
FROM python:3.11-slim AS production

# Create non-root user for security (Doc Brown's requirement)
RUN groupadd -r valis && useradd -r -g valis valis

# Set working directory
WORKDIR /app

# Install nginx for reverse proxy and runtime dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder stage
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy VALIS backend source
COPY . /app/

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/config /var/log/nginx /var/log/supervisor && \
    chown -R valis:valis /app && \
    chown -R valis:valis /var/log/nginx && \
    chown -R valis:valis /var/log/supervisor

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/start.sh /app/start.sh

# Make start script executable
RUN chmod +x /app/start.sh

# Create health check script
COPY docker/healthcheck.sh /app/healthcheck.sh
RUN chmod +x /app/healthcheck.sh

# Expose port 80 for nginx reverse proxy
EXPOSE 80

# Add health check (Doc Brown's requirement)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["/app/healthcheck.sh"]

# Set resource limits in container
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER valis

# Start supervisor to manage nginx + FastAPI
CMD ["/app/start.sh"]
