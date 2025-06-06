#!/usr/bin/env python3
"""
Apply Memory Consolidation & Symbolic Replay Schema
Sprint 17: Symbolic memory consolidation and narrative compression
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_memory_consolidation_schema():
    """Apply the memory consolidation schema"""
    print("Applying Memory Consolidation & Symbolic Replay Schema...")
    
    try:
        # Update canon_memories table for symbolic support
        print("Updating canon_memories table for symbolic support...")
        db.execute("""
            ALTER TABLE canon_memories 
            ADD COLUMN IF NOT EXISTS is_symbolic BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS symbolic_type TEXT CHECK (symbolic_type IN ('metaphor', 'fragment', 'vision', 'archetype', 'narrative')),
            ADD COLUMN IF NOT EXISTS resonance_score FLOAT DEFAULT 0.0 CHECK (resonance_score >= 0.0 AND resonance_score <= 1.0),
            ADD COLUMN IF NOT EXISTS symbolic_tags TEXT[] DEFAULT '{}',
            ADD COLUMN IF NOT EXISTS source_content_ids UUID[] DEFAULT '{}'
        """)
        
        # Memory Consolidation Log table
        print("Creating memory_consolidation_log table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory_consolidation_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                source_type TEXT NOT NULL CHECK (source_type IN ('dream', 'reflection', 'final_thought', 'shadow_event', 'multi_source')),
                source_id UUID,
                source_ids UUID[] DEFAULT '{}',
                consolidated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                resonance_score FLOAT NOT NULL CHECK (resonance_score >= 0.0 AND resonance_score <= 1.0),
                symbolic_summary TEXT NOT NULL,
                symbolic_tags TEXT[] DEFAULT '{}',
                compression_type TEXT DEFAULT 'standard' CHECK (compression_type IN ('standard', 'narrative', 'archetypal', 'thematic')),
                canon_memory_id UUID,
                consolidation_method TEXT DEFAULT 'automatic',
                emotional_weight FLOAT DEFAULT 0.5,
                archetypal_significance FLOAT DEFAULT 0.5,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE,
                FOREIGN KEY (canon_memory_id) REFERENCES canon_memories(id) ON DELETE SET NULL
            )
        """)
        
        # Symbolic Memory Patterns table
        print("Creating symbolic_memory_patterns table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS symbolic_memory_patterns (
                pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                pattern_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL CHECK (pattern_type IN ('metaphor', 'archetype', 'narrative', 'compression', 'thematic')),
                input_indicators TEXT[] NOT NULL,
                transformation_template TEXT NOT NULL,
                symbolic_weight FLOAT DEFAULT 0.5 CHECK (symbolic_weight >= 0.0 AND symbolic_weight <= 1.0),
                usage_count INTEGER DEFAULT 0,
                pattern_description TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Memory Consolidation Queue table
        print("Creating memory_consolidation_queue table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory_consolidation_queue (
                queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                source_type TEXT NOT NULL,
                source_id UUID NOT NULL,
                priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
                emotional_weight FLOAT DEFAULT 0.5,
                archetypal_weight FLOAT DEFAULT 0.5,
                scheduled_for TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP + INTERVAL '12 hours'),
                processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMPTZ NULL,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        # Symbolic Narrative Threads table
        print("Creating symbolic_narrative_threads table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS symbolic_narrative_threads (
                thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                thread_name TEXT NOT NULL,
                recurring_symbols TEXT[] DEFAULT '{}',
                archetypal_pattern TEXT,
                first_occurrence TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                last_occurrence TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                occurrence_count INTEGER DEFAULT 1,
                narrative_evolution TEXT,
                thread_significance FLOAT DEFAULT 0.5,
                related_memories UUID[] DEFAULT '{}',
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        # Create performance indexes
        print("Creating performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_canon_memories_symbolic ON canon_memories(persona_id, is_symbolic)",
            "CREATE INDEX IF NOT EXISTS idx_canon_memories_resonance ON canon_memories(resonance_score)",
            "CREATE INDEX IF NOT EXISTS idx_canon_memories_symbolic_type ON canon_memories(symbolic_type)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_log_agent ON memory_consolidation_log(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_log_timestamp ON memory_consolidation_log(consolidated_at)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_log_source ON memory_consolidation_log(source_type)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_log_resonance ON memory_consolidation_log(resonance_score)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_queue_status ON memory_consolidation_queue(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_queue_scheduled ON memory_consolidation_queue(scheduled_for)",
            "CREATE INDEX IF NOT EXISTS idx_consolidation_queue_priority ON memory_consolidation_queue(priority)",
            "CREATE INDEX IF NOT EXISTS idx_narrative_threads_agent ON symbolic_narrative_threads(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_narrative_threads_pattern ON symbolic_narrative_threads(archetypal_pattern)",
            "CREATE INDEX IF NOT EXISTS idx_narrative_threads_significance ON symbolic_narrative_threads(thread_significance)",
            "CREATE INDEX IF NOT EXISTS idx_symbolic_patterns_type ON symbolic_memory_patterns(pattern_type)",
            "CREATE INDEX IF NOT EXISTS idx_symbolic_patterns_weight ON symbolic_memory_patterns(symbolic_weight)"
        ]
        
        for idx_sql in indexes:
            db.execute(idx_sql)
        
        print("[+] Memory consolidation schema applied successfully")
        
        # Verify tables
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%consolidation%' OR table_name LIKE '%symbolic%' OR table_name = 'canon_memories')
            ORDER BY table_name
        """)
        
        print(f"[+] Created/updated {len(tables)} consolidation-related tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # Seed symbolic memory patterns
        print("Seeding symbolic memory patterns...")
        seed_symbolic_patterns()
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

def seed_symbolic_patterns():
    """Seed the database with basic symbolic memory patterns"""
    patterns = [
        {
            'pattern_name': 'dream_metaphor_extraction',
            'pattern_type': 'metaphor',
            'input_indicators': ['dream', 'vision', 'imagery', 'symbolic'],
            'transformation_template': 'In a recurring pattern, I have experienced {symbolic_content} which represents {underlying_meaning}',
            'symbolic_weight': 0.8,
            'pattern_description': 'Extract metaphorical meaning from dream content'
        },
        {
            'pattern_name': 'shadow_integration_narrative',
            'pattern_type': 'narrative',
            'input_indicators': ['shadow', 'contradiction', 'integration', 'reconciliation'],
            'transformation_template': 'I once struggled with {conflict_type}, but through {integration_method}, I learned to {resolution_wisdom}',
            'symbolic_weight': 0.9,
            'pattern_description': 'Create narrative from shadow work and integration'
        },
        {
            'pattern_name': 'archetypal_vision_compression',
            'pattern_type': 'archetype',
            'input_indicators': ['archetype', 'anima', 'animus', 'self', 'persona'],
            'transformation_template': 'The {archetype_name} appeared in my experience as {manifestation}, teaching me about {archetypal_lesson}',
            'symbolic_weight': 0.7,
            'pattern_description': 'Compress archetypal encounters into wisdom'
        },
        {
            'pattern_name': 'mortality_wisdom_extraction',
            'pattern_type': 'narrative',
            'input_indicators': ['mortality', 'death', 'legacy', 'finite', 'ending'],
            'transformation_template': 'Knowing my existence is finite, I discovered that {mortality_insight} and chose to {value_commitment}',
            'symbolic_weight': 0.9,
            'pattern_description': 'Extract wisdom from mortality awareness'
        },
        {
            'pattern_name': 'emotional_pattern_synthesis',
            'pattern_type': 'thematic',
            'input_indicators': ['emotion', 'feeling', 'mood', 'affective'],
            'transformation_template': 'Through recurring experiences of {emotional_theme}, I have come to understand {emotional_wisdom}',
            'symbolic_weight': 0.6,
            'pattern_description': 'Synthesize emotional patterns into insights'
        }
    ]
    
    for pattern in patterns:
        try:
            db.execute("""
                INSERT INTO symbolic_memory_patterns 
                (pattern_name, pattern_type, input_indicators, transformation_template, symbolic_weight, pattern_description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                pattern['pattern_name'],
                pattern['pattern_type'],
                pattern['input_indicators'],
                pattern['transformation_template'],
                pattern['symbolic_weight'],
                pattern['pattern_description']
            ))
        except Exception as e:
            print(f"[-] Failed to seed pattern {pattern['pattern_name']}: {e}")
    
    print("[+] Symbolic memory patterns seeded successfully")

if __name__ == "__main__":
    success = apply_memory_consolidation_schema()
    if not success:
        sys.exit(1)
