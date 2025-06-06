#!/usr/bin/env python3
from memory.db import db

# Get the final thoughts in detail
final_thoughts = db.query("SELECT * FROM agent_final_thoughts")
print(f'Final thoughts ({len(final_thoughts)}):')

for thought in final_thoughts:
    print(f'\nAgent: {thought["agent_id"]}')
    print(f'Type: {thought["thought_type"]}')
    print(f'Symbolic Weight: {thought["symbolic_weight"]:.3f}')
    print(f'Content:')
    print(f'  {thought["content"]}')
    print('-' * 80)
