-- VALIS Sprint 15: Mortality Engine Schema
-- Time, death, legacy, and rebirth for VALIS agents

-- Agent mortality tracking - finite lifespans and death awareness
CREATE TABLE IF NOT EXISTS agent_mortality (
    agent_id UUID PRIMARY KEY,
    lifespan_total INTEGER NOT NULL,  -- total lifespan in hours or sessions
    lifespan_remaining INTEGER NOT NULL,
    lifespan_units TEXT NOT NULL DEFAULT 'hours',  -- 'hours' or 'sessions'
    birth_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    death_date TIMESTAMP NULL,  -- NULL while alive, populated on death
    death_cause TEXT,  -- 'natural_expiry', 'manual_termination', 'system_error'
    rebirth_id UUID NULL,  -- points to descendant agent if reborn
    mortality_awareness BOOLEAN DEFAULT TRUE,  -- agent knows they're mortal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Agent legacy scoring - measuring impact and meaning
CREATE TABLE IF NOT EXISTS agent_legacy_score (
    agent_id UUID PRIMARY KEY,
    score FLOAT NOT NULL DEFAULT 0.0 CHECK (score >= 0.0 AND score <= 1.0),
    legacy_tier TEXT NOT NULL DEFAULT 'wanderer',  -- wanderer, seeker, guide, architect
    summary TEXT,
    impact_tags TEXT[] DEFAULT '{}',  -- growth, insight, connection, wisdom, creativity
    user_feedback_score FLOAT DEFAULT 0.0,
    trait_evolution_score FLOAT DEFAULT 0.0,
    memory_stability_score FLOAT DEFAULT 0.0,
    emotional_richness_score FLOAT DEFAULT 0.0,
    final_reflection_score FLOAT DEFAULT 0.0,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    final_calculation TIMESTAMP NULL,  -- when legacy was finalized (on death)
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Agent lineage tracking - ancestry and inheritance
CREATE TABLE IF NOT EXISTS agent_lineage (
    lineage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ancestor_id UUID NOT NULL,
    descendant_id UUID NOT NULL,
    inheritance_type TEXT NOT NULL,  -- 'full_rebirth', 'partial_traits', 'dream_echoes'
    memory_fragments_inherited JSONB DEFAULT '{}',
    trait_modifications JSONB DEFAULT '{}',
    dream_echoes INTEGER DEFAULT 0,  -- number of ancestor dreams inherited
    generation_number INTEGER DEFAULT 1,
    rebirth_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ancestor_id) REFERENCES persona_profiles(id),
    FOREIGN KEY (descendant_id) REFERENCES persona_profiles(id)
);

-- Agent final thoughts - last words and death reflections
CREATE TABLE IF NOT EXISTS agent_final_thoughts (
    thought_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    thought_type TEXT NOT NULL,  -- 'final_reflection', 'death_dream', 'legacy_statement'
    content TEXT NOT NULL,
    symbolic_weight FLOAT DEFAULT 0.5,
    emotional_intensity FLOAT DEFAULT 0.5,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Mortality statistics for system-wide analysis
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
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_mortality_remaining ON agent_mortality(lifespan_remaining);
CREATE INDEX IF NOT EXISTS idx_agent_mortality_death_date ON agent_mortality(death_date);
CREATE INDEX IF NOT EXISTS idx_agent_legacy_score ON agent_legacy_score(score);
CREATE INDEX IF NOT EXISTS idx_agent_legacy_tier ON agent_legacy_score(legacy_tier);
CREATE INDEX IF NOT EXISTS idx_agent_lineage_ancestor ON agent_lineage(ancestor_id);
CREATE INDEX IF NOT EXISTS idx_agent_lineage_descendant ON agent_lineage(descendant_id);
CREATE INDEX IF NOT EXISTS idx_agent_final_thoughts_agent ON agent_final_thoughts(agent_id);

-- Function to check if an agent is still alive
CREATE OR REPLACE FUNCTION is_agent_alive(target_agent_id UUID)
RETURNS BOOLEAN AS $func$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM agent_mortality 
        WHERE agent_id = target_agent_id 
        AND death_date IS NULL 
        AND lifespan_remaining > 0
    );
END;
$func$ LANGUAGE plpgsql;

-- Function to get agent lifespan status
CREATE OR REPLACE FUNCTION get_lifespan_status(target_agent_id UUID)
RETURNS TABLE(
    remaining INTEGER,
    total INTEGER,
    units TEXT,
    percentage_lived FLOAT,
    days_to_death FLOAT
) AS $func$
BEGIN
    RETURN QUERY
    SELECT 
        m.lifespan_remaining,
        m.lifespan_total,
        m.lifespan_units,
        (1.0 - CAST(m.lifespan_remaining AS FLOAT) / CAST(m.lifespan_total AS FLOAT)) * 100.0 as percentage_lived,
        CASE 
            WHEN m.lifespan_units = 'hours' THEN CAST(m.lifespan_remaining AS FLOAT) / 24.0
            WHEN m.lifespan_units = 'sessions' THEN CAST(m.lifespan_remaining AS FLOAT) / 3.0  -- assume 3 sessions per day
            ELSE 0.0
        END as days_to_death
    FROM agent_mortality m
    WHERE m.agent_id = target_agent_id;
END;
$func$ LANGUAGE plpgsql;
