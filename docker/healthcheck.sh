#!/bin/bash
# VALIS Health Check Script
# Doc Brown's Temporal Service Monitoring

# Check if nginx is responding
nginx_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")

# Check if FastAPI backend is responding
backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health || echo "000")

# Both services must be healthy
if [ "$nginx_status" = "200" ] && [ "$backend_status" = "200" ]; then
    echo "✅ VALIS services healthy: nginx($nginx_status) backend($backend_status)"
    exit 0
else
    echo "❌ VALIS services unhealthy: nginx($nginx_status) backend($backend_status)"
    exit 1
fi
