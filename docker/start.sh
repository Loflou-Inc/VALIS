#!/bin/bash
# VALIS Container Startup Script
# Doc Brown's Temporal Service Orchestration

set -e

echo "🚀 Starting VALIS Containerized Deployment..."

# Ensure proper permissions
chown -R valis:valis /app/logs /app/config

# Validate essential files exist
if [ ! -f "/app/config.json" ]; then
    echo "⚠️ No config.json found, creating default..."
    cp /app/config.json.example /app/config.json 2>/dev/null || echo "{}" > /app/config.json
fi

if [ ! -f "/app/.env" ]; then
    echo "⚠️ No .env file found, creating default..."
    echo "# VALIS Environment Variables" > /app/.env
    echo "OPENAI_API_KEY=your_openai_key_here" >> /app/.env
    echo "ANTHROPIC_API_KEY=your_anthropic_key_here" >> /app/.env
fi

# Start supervisor to manage services
echo "🔧 Starting Supervisor (nginx + FastAPI backend)..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
