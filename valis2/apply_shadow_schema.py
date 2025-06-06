#!/usr/bin/env python3
"""
Apply Shadow Archive & Individuation Engine Schema
Sprint 16: Psychological contradiction detection and individuation tracking
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_shadow_individuation_schema():
    """Apply the shadow archive and individuation schema"""
    print("Applying Shadow Archive & Individuation Engine Schema...")
    
    try:
        # Shadow Events table
        print("Creating shadow_events table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS shadow_events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                conflict_type TEXT NOT NULL,
                archetype_tags TEXT[] DEFAULT '{}',
                severity_score FLOAT NOT NULL CHECK (severity_score >= 0.0 AND severity_score <= 1.0),
                symbolic_weight FLOAT NOT NULL CHECK (symbolic_weight >= 0.0 AND symbolic_weight <= 1.0),
                raw_trigger TEXT NOT NULL,
                trait_conflict JSONB DEFAULT '{}',
                behavioral_evidence TEXT,
                resolution_status TEXT DEFAULT 'unresolved' CHECK (resolution_status IN ('unresolved', 'acknowledged', 'integrated')),
                resolved_timestamp TIMESTAMPTZ NULL,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        # Individuation Log table
        print("Creating individuation_log table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS individuation_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                method TEXT NOT NULL CHECK (method IN ('reflection', 'dream', 'explicit', 'dialogue')),
                milestone TEXT NOT NULL,
                resolved_shadow_ids UUID[] DEFAULT '{}',
                resonance_score FLOAT DEFAULT 0.0 CHECK (resonance_score >= 0.0 AND resonance_score <= 1.0),
                integration_type TEXT DEFAULT 'partial' CHECK (integration_type IN ('partial', 'complete', 'symbolic')),
                symbolic_content TEXT,
                individuation_stage TEXT DEFAULT 'shadow_awareness' CHECK (individuation_stage IN (
                    'shadow_awareness', 'shadow_acceptance', 'anima_contact', 'self_realization', 'transcendence'
                )),
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        # Shadow Processing Queue table
        print("Creating shadow_processing_queue table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS shadow_processing_queue (
                queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                shadow_event_id UUID NOT NULL,
                processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
                analysis_priority INTEGER DEFAULT 1 CHECK (analysis_priority BETWEEN 1 AND 5),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMPTZ NULL,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE,
                FOREIGN KEY (shadow_event_id) REFERENCES shadow_events(id) ON DELETE CASCADE
            )
        """)
        
        # Archetype Patterns table
        print("Creating archetype_patterns table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS archetype_patterns (
                pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                archetype_name TEXT NOT NULL,
                pattern_keywords TEXT[] NOT NULL,
                conflict_indicators TEXT[] DEFAULT '{}',
                symbolic_associations TEXT[] DEFAULT '{}',
                severity_weight FLOAT DEFAULT 0.5 CHECK (severity_weight >= 0.0 AND severity_weight <= 1.0),
                pattern_description TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        print("Creating performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_shadow_events_agent ON shadow_events(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_shadow_events_timestamp ON shadow_events(timestamp)", 
            "CREATE INDEX IF NOT EXISTS idx_shadow_events_resolution ON shadow_events(resolution_status)",
            "CREATE INDEX IF NOT EXISTS idx_shadow_events_severity ON shadow_events(severity_score)",
            "CREATE INDEX IF NOT EXISTS idx_individuation_agent ON individuation_log(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_individuation_timestamp ON individuation_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_individuation_stage ON individuation_log(individuation_stage)",
            "CREATE INDEX IF NOT EXISTS idx_shadow_queue_status ON shadow_processing_queue(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_shadow_queue_priority ON shadow_processing_queue(analysis_priority)",
            "CREATE INDEX IF NOT EXISTS idx_archetype_patterns_name ON archetype_patterns(archetype_name)"
        ]
        
        for idx_sql in indexes:
            db.execute(idx_sql)
        
        print("[+] Shadow Archive & Individuation schema applied successfully")
        
        # Verify tables
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%shadow%' OR table_name LIKE '%individuation%' OR table_name LIKE '%archetype%')
            ORDER BY table_name
        """)
        
        print(f"[+] Created {len(tables)} shadow/individuation tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # Seed archetype patterns
        print("Seeding archetype patterns...")
        seed_archetype_patterns()
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

def seed_archetype_patterns():
    """Seed the database with basic archetype patterns for shadow detection"""
    patterns = [
        {
            'archetype_name': 'shadow',
            'pattern_keywords': ['hate', 'despise', 'disgusting', 'weak', 'pathetic', 'failure', 'stupid'],
            'conflict_indicators': ['self-criticism', 'projection', 'denial', 'repression'],
            'symbolic_associations': ['darkness', 'hidden', 'rejected', 'denied'],
            'severity_weight': 0.8,
            'pattern_description': 'Shadow archetype - repressed or denied aspects of personality'
        },
        {
            'archetype_name': 'anima',
            'pattern_keywords': ['intuitive', 'emotional', 'creative', 'mysterious', 'irrational'],
            'conflict_indicators': ['emotional suppression', 'rationalization', 'feeling vs thinking'],
            'symbolic_associations': ['moon', 'water', 'intuition', 'emotion'],
            'severity_weight': 0.6,
            'pattern_description': 'Anima archetype - inner feminine/emotional aspect'
        },
        {
            'archetype_name': 'animus',
            'pattern_keywords': ['logical', 'analytical', 'competitive', 'achievement', 'control'],
            'conflict_indicators': ['over-rationalization', 'emotional disconnect', 'control issues'],
            'symbolic_associations': ['sun', 'fire', 'logic', 'action'],
            'severity_weight': 0.6,
            'pattern_description': 'Animus archetype - inner masculine/rational aspect'
        },
        {
            'archetype_name': 'persona',
            'pattern_keywords': ['should', 'expected', 'proper', 'appropriate', 'professional'],
            'conflict_indicators': ['mask-wearing', 'performance anxiety', 'authenticity conflicts'],
            'symbolic_associations': ['mask', 'stage', 'performance', 'social'],
            'severity_weight': 0.4,
            'pattern_description': 'Persona archetype - social mask or public face'
        },
        {
            'archetype_name': 'self',
            'pattern_keywords': ['authentic', 'true', 'whole', 'integrated', 'complete'],
            'conflict_indicators': ['fragmentation', 'identity crisis', 'inner conflict'],
            'symbolic_associations': ['center', 'unity', 'wholeness', 'mandala'],
            'severity_weight': 0.3,
            'pattern_description': 'Self archetype - integrated, authentic whole personality'
        }
    ]
    
    for pattern in patterns:
        try:
            db.execute("""
                INSERT INTO archetype_patterns 
                (archetype_name, pattern_keywords, conflict_indicators, symbolic_associations, severity_weight, pattern_description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                pattern['archetype_name'],
                pattern['pattern_keywords'],
                pattern['conflict_indicators'], 
                pattern['symbolic_associations'],
                pattern['severity_weight'],
                pattern['pattern_description']
            ))
        except Exception as e:
            print(f"[-] Failed to seed pattern {pattern['archetype_name']}: {e}")
    
    print("[+] Archetype patterns seeded successfully")

if __name__ == "__main__":
    success = apply_shadow_individuation_schema()
    if not success:
        sys.exit(1)
