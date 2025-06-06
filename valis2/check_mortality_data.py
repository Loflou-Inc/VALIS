#!/usr/bin/env python3
from memory.db import db

# Check for dead agents
dead_agents = db.query("SELECT * FROM agent_mortality WHERE death_date IS NOT NULL")
print(f'Dead agents ({len(dead_agents)}):')
for agent in dead_agents:
    print(f'  {agent["agent_id"]} - died {agent["death_date"]} - cause: {agent["death_cause"]}')

# Check lineage data
lineage = db.query("SELECT * FROM agent_lineage LIMIT 5")
print(f'\nLineage records ({len(lineage)}):')
for line in lineage:
    print(f'  {line["ancestor_id"]} -> {line["descendant_id"]}')
    print(f'    Inherited: {line["memory_fragments_inherited"]}')

# Check final thoughts
final_thoughts = db.query("SELECT * FROM agent_final_thoughts LIMIT 3")
print(f'\nFinal thoughts ({len(final_thoughts)}):')
for thought in final_thoughts:
    print(f'  {thought["agent_id"]} - {thought["thought_type"]}')
    print(f'    Content: {thought["content"][:100]}...')
