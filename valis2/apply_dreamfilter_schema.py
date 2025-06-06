#!/usr/bin/env python3
"""
Apply DreamFilter Schema to VALIS Database
Sprint 14: The DreamFilter - Unconscious Symbolic Expression
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_dreamfilter_schema():
    """Apply the dreamfilter schema to the database"""
    print("Applying DreamFilter Schema...")
    
    try:
        # Execute each table creation manually to avoid parsing issues
        print("Creating unconscious_log table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS unconscious_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                dream_type TEXT NOT NULL,
                content TEXT NOT NULL,
                source_summary JSONB,
                symbolic_weight FLOAT DEFAULT 1.0,
                emotional_resonance FLOAT DEFAULT 0.5,
                archetype_tags JSONB DEFAULT '[]',
                session_trigger TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating dream_schedule table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS dream_schedule (
                agent_id UUID PRIMARY KEY,
                last_dream_time TIMESTAMP,
                next_dream_due TIMESTAMP,
                dream_frequency_hours INTEGER DEFAULT 6,
                idle_threshold_minutes INTEGER DEFAULT 3,
                dream_enabled BOOLEAN DEFAULT TRUE,
                consecutive_dreams INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating dream_patterns table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS dream_patterns (
                pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_description TEXT,
                occurrences INTEGER DEFAULT 1,
                first_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_unconscious_log_agent ON unconscious_log(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_unconscious_log_timestamp ON unconscious_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_unconscious_log_dream_type ON unconscious_log(dream_type)",
            "CREATE INDEX IF NOT EXISTS idx_dream_schedule_next_due ON dream_schedule(next_dream_due)",
            "CREATE INDEX IF NOT EXISTS idx_dream_patterns_agent ON dream_patterns(agent_id)"
        ]
        
        for idx_sql in indexes:
            db.execute(idx_sql)
        
        print(f"[+] DreamFilter schema applied successfully")
        
        # Verify tables were created
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('unconscious_log', 'dream_schedule', 'dream_patterns')
            ORDER BY table_name
        """)
        
        print(f"[+] Created {len(tables)} dreamfilter tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # Initialize dream schedules for existing personas
        try:
            db.execute("""
                INSERT INTO dream_schedule (agent_id, last_dream_time, next_dream_due)
                SELECT 
                    id as agent_id,
                    NOW() - INTERVAL '1 hour' as last_dream_time,
                    NOW() + INTERVAL '30 minutes' as next_dream_due
                FROM persona_profiles
                WHERE id NOT IN (SELECT agent_id FROM dream_schedule)
            """)
            
            # Check dream schedules were initialized
            schedules = db.query("SELECT COUNT(*) as count FROM dream_schedule")[0]['count']
            print(f"[+] Initialized {schedules} dream schedules")
            
        except Exception as e:
            print(f"[-] Dream schedule initialization failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_dreamfilter_schema()
    if not success:
        sys.exit(1)
