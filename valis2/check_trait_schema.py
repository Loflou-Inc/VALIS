#!/usr/bin/env python3
from memory.db import db

# Check trait history table schema
schema = db.query("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'agent_trait_history'
    ORDER BY ordinal_position
""")

print('agent_trait_history table schema:')
for col in schema:
    print(f'  {col["column_name"]} - {col["data_type"]} ({col["is_nullable"]})')

# Check recent trait changes
recent = db.query("SELECT * FROM agent_trait_history ORDER BY timestamp DESC LIMIT 5")
print(f'\nRecent trait changes ({len(recent)} records):')
for r in recent:
    print(f'  {r["trait"]}: {r["value_before"]:.3f} -> {r["value_after"]:.3f} ({r["source_event"]})')
