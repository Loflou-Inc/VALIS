#!/usr/bin/env python3
from memory.db import db

# Check dream schedule table
schedule = db.query("SELECT * FROM dream_schedule LIMIT 5")
print(f'Dream schedule entries ({len(schedule)}):')
for s in schedule:
    print(f'  Agent: {s["agent_id"]}')
    print(f'  Next due: {s["next_dream_due"]}')
    print(f'  Frequency: {s["dream_frequency_hours"]} hours')
    print(f'  Consecutive: {s["consecutive_dreams"]}')
    print()

# Check dream patterns
patterns = db.query("SELECT * FROM dream_patterns LIMIT 3")
print(f'Dream patterns ({len(patterns)}):')
for p in patterns:
    print(f'  {p}')
