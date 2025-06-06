#!/usr/bin/env python3
from memory.db import db

# Check mortality-related tables
mortality_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%mortality%'")
print('Mortality tables:')
for t in mortality_tables:
    print(f'  {t["table_name"]}')

# Check legacy tables
legacy_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%legacy%'")
print('\nLegacy tables:')
for t in legacy_tables:
    print(f'  {t["table_name"]}')

# Check lineage tables
lineage_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%lineage%'")
print('\nLineage tables:')
for t in lineage_tables:
    print(f'  {t["table_name"]}')

# Check agent mortality data
try:
    mortality_data = db.query("SELECT agent_id, lifespan_remaining, lifespan_total FROM agent_mortality LIMIT 5")
    print(f'\nMortality data ({len(mortality_data)} agents):')
    for m in mortality_data:
        print(f'  {m["agent_id"]}: {m["lifespan_remaining"]}/{m["lifespan_total"]} remaining')
except Exception as e:
    print(f'Error checking mortality data: {e}')
