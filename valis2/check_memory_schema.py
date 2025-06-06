#!/usr/bin/env python3
from memory.db import db

# Check canon_memories schema
schema = db.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'canon_memories' ORDER BY ordinal_position")
print('Canon memories schema:')
for col in schema:
    print(f'  {col["column_name"]} - {col["data_type"]}')

# Get a sample canon memory
sample = db.query("SELECT * FROM canon_memories WHERE is_symbolic = true LIMIT 1")
if sample:
    print(f'\nSample symbolic memory:')
    print(f'  Keys: {list(sample[0].keys())}')
    print(f'  Data: {sample[0]}')
else:
    print('\nNo symbolic memories found')

# Check consolidation log sample
cons_sample = db.query("SELECT * FROM memory_consolidation_log LIMIT 1")
if cons_sample:
    print(f'\nSample consolidation log:')
    print(f'  Data: {cons_sample[0]}')
