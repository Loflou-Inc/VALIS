#!/usr/bin/env python3
from memory.db import db

# Check consolidation-related tables
consolidation_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%consolidation%'")
print('Consolidation tables:')
for t in consolidation_tables:
    print(f'  {t["table_name"]}')

# Check symbolic memory tables
symbolic_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%symbolic%'")
print('\nSymbolic memory tables:')
for t in symbolic_tables:
    print(f'  {t["table_name"]}')

# Check if canon_memories has symbolic columns
try:
    schema = db.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'canon_memories' AND column_name LIKE '%symbolic%'")
    print(f'\nCanon memories symbolic columns:')
    for col in schema:
        print(f'  {col["column_name"]} - {col["data_type"]}')
except Exception as e:
    print(f'Error checking canon_memories schema: {e}')

# Check consolidation log entries
try:
    consolidations = db.query("SELECT * FROM memory_consolidation_log ORDER BY consolidated_at DESC LIMIT 5")
    print(f'\nRecent consolidations ({len(consolidations)}):')
    for cons in consolidations:
        print(f'  {cons["agent_id"]}: {cons["source_type"]} -> {cons["symbolic_summary"][:60]}...')
        print(f'    Resonance: {cons["resonance_score"]:.3f}')
except Exception as e:
    print(f'Error checking consolidation log: {e}')
