#!/usr/bin/env python3
from memory.db import db

# Count symbolic memories by type
symbolic_counts = db.query("""
    SELECT symbolic_type, COUNT(*) as count, AVG(resonance_score) as avg_resonance
    FROM canon_memories 
    WHERE is_symbolic = true 
    GROUP BY symbolic_type
    ORDER BY count DESC
""")

print('Symbolic memory distribution:')
for row in symbolic_counts:
    print(f'  {row["symbolic_type"]}: {row["count"]} memories (avg resonance: {row["avg_resonance"]:.3f})')

# Get total counts
total_memories = db.query("SELECT COUNT(*) as count FROM canon_memories")[0]['count']
symbolic_memories = db.query("SELECT COUNT(*) as count FROM canon_memories WHERE is_symbolic = true")[0]['count']
total_consolidations = db.query("SELECT COUNT(*) as count FROM memory_consolidation_log")[0]['count']
total_threads = db.query("SELECT COUNT(*) as count FROM symbolic_narrative_threads")[0]['count']

print(f'\nSystem statistics:')
print(f'  Total canon memories: {total_memories}')
print(f'  Symbolic memories: {symbolic_memories}')
print(f'  Total consolidations: {total_consolidations}')
print(f'  Narrative threads: {total_threads}')

# Show recent symbolic memories
recent_symbolic = db.query("""
    SELECT persona_id, symbolic_type, content, resonance_score 
    FROM canon_memories 
    WHERE is_symbolic = true 
    ORDER BY created_at DESC 
    LIMIT 5
""")

print(f'\nRecent symbolic memories:')
for memory in recent_symbolic:
    print(f'  {memory["persona_id"]}: {memory["symbolic_type"]} (resonance: {memory["resonance_score"]:.3f})')
    print(f'    Content: {memory["content"][:100]}...')
