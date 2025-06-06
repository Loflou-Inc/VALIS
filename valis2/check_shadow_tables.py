#!/usr/bin/env python3
from memory.db import db

# Check shadow-related tables
shadow_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%shadow%'")
print('Shadow tables:')
for t in shadow_tables:
    print(f'  {t["table_name"]}')

# Check individuation tables
individuation_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%individuation%'")
print('\nIndividuation tables:')
for t in individuation_tables:
    print(f'  {t["table_name"]}')

# Check archetype tables
archetype_tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%archetype%'")
print('\nArchetype tables:')
for t in archetype_tables:
    print(f'  {t["table_name"]}')

# Check for shadow events
try:
    shadow_events = db.query("SELECT * FROM shadow_events LIMIT 5")
    print(f'\nShadow events ({len(shadow_events)}):')
    for event in shadow_events:
        print(f'  {event["agent_id"]}: {event["conflict_type"]} - severity {event["severity_score"]:.3f}')
        print(f'    Archetypes: {event["archetype_tags"]}')
except Exception as e:
    print(f'Error checking shadow events: {e}')
