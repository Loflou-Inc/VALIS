#!/usr/bin/env python3
from memory.db import db

# Check legacy scores for all agents
legacy_scores = db.query("SELECT agent_id, score, legacy_tier, summary FROM agent_legacy_score ORDER BY score DESC")
print(f'Legacy scores ({len(legacy_scores)} agents):')
for score in legacy_scores:
    print(f'  {score["legacy_tier"].upper()}: {score["score"]:.3f} - {score["summary"][:80]}...')

# Check mortality statistics
try:
    stats = db.query("SELECT * FROM mortality_statistics LIMIT 5")
    print(f'\nMortality statistics ({len(stats)}):')
    for stat in stats:
        print(f'  {stat}')
except Exception as e:
    print(f'No mortality statistics found: {e}')
