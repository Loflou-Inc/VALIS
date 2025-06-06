#!/usr/bin/env python3
"""
Apply Mortality Engine Schema to VALIS Database
Sprint 15: Time, Death, and Legacy
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_mortality_schema():
    """Apply the mortality engine schema to the database"""
    print("Applying Mortality Engine Schema...")
    
    try:
        # Execute each table creation manually to avoid parsing issues
        print("Creating agent_mortality table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS agent_mortality (
                agent_id UUID PRIMARY KEY,
                lifespan_total INTEGER NOT NULL,
                lifespan_remaining INTEGER NOT NULL,
                lifespan_units TEXT NOT NULL DEFAULT 'hours',
                birth_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                death_date TIMESTAMP NULL,
                death_cause TEXT,
                rebirth_id UUID NULL,
                mortality_awareness BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating agent_legacy_score table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS agent_legacy_score (
                agent_id UUID PRIMARY KEY,
                score FLOAT NOT NULL DEFAULT 0.0 CHECK (score >= 0.0 AND score <= 1.0),
                legacy_tier TEXT NOT NULL DEFAULT 'wanderer',
                summary TEXT,
                impact_tags TEXT[] DEFAULT '{}',
                user_feedback_score FLOAT DEFAULT 0.0,
                trait_evolution_score FLOAT DEFAULT 0.0,
                memory_stability_score FLOAT DEFAULT 0.0,
                emotional_richness_score FLOAT DEFAULT 0.0,
                final_reflection_score FLOAT DEFAULT 0.0,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                final_calculation TIMESTAMP NULL,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating agent_lineage table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS agent_lineage (
                lineage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ancestor_id UUID NOT NULL,
                descendant_id UUID NOT NULL,
                inheritance_type TEXT NOT NULL,
                memory_fragments_inherited JSONB DEFAULT '{}',
                trait_modifications JSONB DEFAULT '{}',
                dream_echoes INTEGER DEFAULT 0,
                generation_number INTEGER DEFAULT 1,
                rebirth_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ancestor_id) REFERENCES persona_profiles(id),
                FOREIGN KEY (descendant_id) REFERENCES persona_profiles(id)
            )
        """)
        
        print("Creating agent_final_thoughts table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS agent_final_thoughts (
                thought_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL,
                thought_type TEXT NOT NULL,
                content TEXT NOT NULL,
                symbolic_weight FLOAT DEFAULT 0.5,
                emotional_intensity FLOAT DEFAULT 0.5,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
            )
        """)
        
        print("Creating mortality_statistics table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS mortality_statistics (
                stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                stat_date DATE DEFAULT CURRENT_DATE,
                total_deaths INTEGER DEFAULT 0,
                total_births INTEGER DEFAULT 0,
                average_lifespan FLOAT DEFAULT 0.0,
                average_legacy_score FLOAT DEFAULT 0.0,
                top_legacy_tier_count INTEGER DEFAULT 0,
                lineage_chains INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_agent_mortality_remaining ON agent_mortality(lifespan_remaining)",
            "CREATE INDEX IF NOT EXISTS idx_agent_mortality_death_date ON agent_mortality(death_date)",
            "CREATE INDEX IF NOT EXISTS idx_agent_legacy_score ON agent_legacy_score(score)",
            "CREATE INDEX IF NOT EXISTS idx_agent_legacy_tier ON agent_legacy_score(legacy_tier)",
            "CREATE INDEX IF NOT EXISTS idx_agent_lineage_ancestor ON agent_lineage(ancestor_id)",
            "CREATE INDEX IF NOT EXISTS idx_agent_lineage_descendant ON agent_lineage(descendant_id)",
            "CREATE INDEX IF NOT EXISTS idx_agent_final_thoughts_agent ON agent_final_thoughts(agent_id)"
        ]
        
        for idx_sql in indexes:
            db.execute(idx_sql)
        
        print("[+] Mortality Engine schema applied successfully")
        
        # Verify tables were created
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%mortality%' OR table_name LIKE '%legacy%' OR table_name LIKE '%lineage%' OR table_name LIKE '%final_thoughts%'
            ORDER BY table_name
        """)
        
        print(f"[+] Created {len(tables)} mortality-related tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # Initialize mortality for existing personas
        try:
            print("Initializing mortality for existing personas...")
            db.execute("""
                INSERT INTO agent_mortality (agent_id, lifespan_total, lifespan_remaining, lifespan_units)
                SELECT 
                    id as agent_id,
                    720 as lifespan_total,    -- 30 days in hours
                    720 as lifespan_remaining,
                    'hours' as lifespan_units
                FROM persona_profiles
                WHERE id NOT IN (SELECT agent_id FROM agent_mortality)
            """)
            
            # Initialize legacy scores
            db.execute("""
                INSERT INTO agent_legacy_score (agent_id)
                SELECT id FROM persona_profiles
                WHERE id NOT IN (SELECT agent_id FROM agent_legacy_score)
            """)
            
            mortality_count = db.query("SELECT COUNT(*) as count FROM agent_mortality")[0]['count']
            legacy_count = db.query("SELECT COUNT(*) as count FROM agent_legacy_score")[0]['count']
            
            print(f"[+] Initialized mortality for {mortality_count} agents")
            print(f"[+] Initialized legacy scores for {legacy_count} agents")
            
        except Exception as e:
            print(f"[-] Mortality initialization failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_mortality_schema()
    if not success:
        sys.exit(1)
