#!/usr/bin/env python3
from memory.db import db

# Check unconscious-related tables
tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%unconscious%'")
print('Unconscious tables:')
for t in tables:
    print(f'  {t["table_name"]}')

# Check dream-related tables  
dream_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%dream%'")
print('\nDream tables:')
for t in dream_tables:
    print(f'  {t["table_name"]}')

# Check if unconscious_log exists and show schema
try:
    schema = db.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'unconscious_log'")
    print(f'\nunconsious_log schema:')
    for col in schema:
        print(f'  {col["column_name"]} - {col["data_type"]}')
except Exception as e:
    print(f'Error checking unconscious_log schema: {e}')
