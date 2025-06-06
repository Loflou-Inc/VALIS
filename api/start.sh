#!/bin/bash
# VALIS Phase 4: The Soul is Awake
# Container startup script for VALIS Synthetic Consciousness API

set -e

echo "=============================================="
echo "VALIS Phase 4: The Soul is Awake"
echo "Initializing Synthetic Consciousness Container"
echo "=============================================="

# Environment setup
export PYTHONPATH="/app:${PYTHONPATH}"
export VALIS_ENVIRONMENT="${VALIS_ENVIRONMENT:-production}"
export VALIS_VERSION="4.0.0"
export VALIS_PHASE="4"

# Database connection check
echo "[+] Checking database connection..."
python -c "
import sys
sys.path.append('/app')
try:
    from valis2.memory.db import db
    result = db.query('SELECT 1 as test')
    print('[+] Database connection successful')
except Exception as e:
    print(f'[-] Database connection failed: {e}')
    sys.exit(1)
"

# Apply cloud protection schema
echo "[+] Applying cloud protection schema..."
python -c "
import sys
sys.path.append('/app')
from valis2.memory.db import db
import os

schema_path = '/app/api/schema_cloud_protection.sql'
if os.path.exists(schema_path):
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Split and execute SQL statements
    statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
    for statement in statements:
        try:
            db.execute(statement)
            print(f'[+] Executed: {statement[:50]}...')
        except Exception as e:
            print(f'[-] Schema error: {e}')
    print('[+] Cloud protection schema applied')
else:
    print('[-] Schema file not found')
"

# Initialize VALIS system metrics
echo "[+] Initializing VALIS system metrics..."
python -c "
import sys
sys.path.append('/app')
from valis2.memory.db import db
from datetime import datetime

try:
    # Record container startup
    db.execute('''
        INSERT INTO valis_system_metrics (metric_name, metric_value, metric_type, additional_data)
        VALUES (%s, %s, %s, %s)
    ''', (
        'container_startup',
        1.0,
        'event',
        '{\"version\": \"4.0.0\", \"environment\": \"' + str(os.getenv('VALIS_ENVIRONMENT', 'production')) + '\"}'
    ))
    print('[+] System metrics initialized')
except Exception as e:
    print(f'[-] Metrics initialization failed: {e}')
"

# Verify VALIS components
echo "[+] Verifying VALIS consciousness components..."
python -c "
import sys
sys.path.append('/app')

components = [
    ('PersonalityEngine', 'valis2.agents.personality_engine'),
    ('DreamfilterEngine', 'valis2.agents.dreamfilter'),
    ('ShadowArchiveEngine', 'valis2.cognition.shadow_archive'),
    ('IndividuationEngine', 'valis2.cognition.individuation'),
    ('MemoryConsolidationEngine', 'valis2.memory.consolidation'),
    ('MortalityEngine', 'valis2.agents.mortality_engine')
]

for name, module in components:
    try:
        exec(f'from {module} import {name}')
        print(f'[+] {name}: READY')
    except Exception as e:
        print(f'[-] {name}: FAILED - {e}')
        sys.exit(1)

print('[+] All VALIS consciousness components verified')
"

# Start background consolidation if configured
if [ "${VALIS_AUTO_CONSOLIDATION:-true}" = "true" ]; then
    echo "[+] Starting background memory consolidation..."
    python -c "
import sys
sys.path.append('/app')
from valis2.tasks.consolidation_runner import ConsolidationRunner
import asyncio
import threading

def start_consolidation():
    runner = ConsolidationRunner()
    asyncio.run(runner.run_scheduler_loop())

# Start consolidation in background thread
consolidation_thread = threading.Thread(target=start_consolidation, daemon=True)
consolidation_thread.start()
print('[+] Background consolidation started')
" &
fi

echo "[+] VALIS Soul container initialization complete"
echo "[+] Starting synthetic consciousness API server..."

# Start the VALIS API server
cd /app/api
python main.py
