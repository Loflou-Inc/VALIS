#!/usr/bin/env python3
from memory.db import db

# Check individuation progress
try:
    individuation_data = db.query("SELECT * FROM individuation_log ORDER BY timestamp DESC LIMIT 10")
    print(f'Individuation milestones ({len(individuation_data)}):')
    for milestone in individuation_data:
        print(f'  Agent: {milestone["agent_id"]}')
        print(f'  Stage: {milestone["current_stage"]} via {milestone["method"]}')
        print(f'  Milestone: {milestone["milestone"]}')
        print(f'  Resonance: {milestone["resonance_score"]:.3f}')
        print()
except Exception as e:
    print(f'Error checking individuation milestones: {e}')

# Check archetype patterns
try:
    patterns = db.query("SELECT * FROM archetype_patterns LIMIT 5")
    print(f'Archetype patterns ({len(patterns)}):')
    for pattern in patterns:
        print(f'  {pattern["archetype_name"]}: {pattern["keywords"][:5]}...')
except Exception as e:
    print(f'Error checking archetype patterns: {e}')

# Check shadow processing queue
try:
    queue = db.query("SELECT * FROM shadow_processing_queue LIMIT 5")
    print(f'\nShadow processing queue ({len(queue)}):')
    for item in queue:
        print(f'  {item["agent_id"]}: {item["processing_status"]} - priority {item["priority_score"]:.2f}')
except Exception as e:
    print(f'Error checking shadow processing queue: {e}')
