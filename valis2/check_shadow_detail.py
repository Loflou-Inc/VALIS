#!/usr/bin/env python3
from memory.db import db

# Check archetype patterns schema
schema = db.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'archetype_patterns'")
print('Archetype patterns schema:')
for col in schema:
    print(f'  {col["column_name"]} - {col["data_type"]}')

# Get archetype data 
patterns = db.query("SELECT * FROM archetype_patterns LIMIT 3")
print(f'\nArchetype patterns ({len(patterns)}):')
for pattern in patterns:
    print(f'  Pattern: {pattern}')

# Check what shadow events look like in detail
shadow_detail = db.query("SELECT * FROM shadow_events LIMIT 2")
print(f'\nShadow events detail ({len(shadow_detail)}):')
for event in shadow_detail:
    print(f'  Event: {event}')
    print()
