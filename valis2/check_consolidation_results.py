#!/usr/bin/env python3
from memory.db import db

# Check symbolic memories in canon_memories
symbolic_memories = db.query("SELECT * FROM canon_memories WHERE is_symbolic = true ORDER BY created_at DESC LIMIT 10")
print(f'Symbolic memories ({len(symbolic_memories)}):')
for memory in symbolic_memories:
    print(f'  {memory["agent_id"]}: {memory["symbolic_type"]} - {memory["content"][:80]}...')
    print(f'    Resonance: {memory.get("resonance_score", "N/A")}')
    print()

# Check narrative threads
threads = db.query("SELECT * FROM symbolic_narrative_threads LIMIT 5")
print(f'Narrative threads ({len(threads)}):')
for thread in threads:
    print(f'  {thread["agent_id"]}: {thread["thread_name"]} ({thread["occurrence_count"]} occurrences)')
    print(f'    Pattern: {thread["symbolic_pattern"][:60]}...')
    print()

# Check consolidation statistics
total_consolidations = db.query("SELECT COUNT(*) as count FROM memory_consolidation_log")[0]['count']
avg_resonance = db.query("SELECT AVG(resonance_score) as avg FROM memory_consolidation_log")[0]['avg']

print(f'System statistics:')
print(f'  Total consolidations: {total_consolidations}')
print(f'  Average resonance: {avg_resonance:.3f if avg_resonance else 0}')
