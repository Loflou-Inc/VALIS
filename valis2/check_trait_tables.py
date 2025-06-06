#!/usr/bin/env python3
from memory.db import db

# Check trait-related tables
tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%trait%'")
print('Trait-related tables:')
for t in tables:
    print(f'  {t["table_name"]}')

# Check if trait history table exists
history = db.query("SELECT * FROM agent_trait_history LIMIT 3")
print(f'\nTrait history records: {len(history)}')
for h in history:
    print(f'  {h["persona_id"]} - {h["trait"]}: {h["value_before"]} -> {h["value_after"]} ({h["source_event"]})')
