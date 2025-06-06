-- VALIS Sprint 13: Trait History and Evolution Schema
-- Track personality trait changes over time

-- Agent trait history for tracking personality evolution
CREATE TABLE IF NOT EXISTS agent_trait_history (
    history_id SERIAL PRIMARY KEY,
    persona_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    trait TEXT NOT NULL,  -- Big Five trait name (extraversion, agreeableness, etc.)
    value_before FLOAT NOT NULL,
    value_after FLOAT NOT NULL,
    delta FLOAT NOT NULL,
    source_event TEXT NOT NULL,  -- feedback, dialogue, reflection, decay
    influence_strength FLOAT DEFAULT 1.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Add evolving_traits column to existing personality profiles
ALTER TABLE agent_personality_profiles 
ADD COLUMN IF NOT EXISTS evolving_traits JSONB DEFAULT '{}';

-- Add trait evolution metadata
ALTER TABLE agent_personality_profiles
ADD COLUMN IF NOT EXISTS evolution_rate FLOAT DEFAULT 0.1,
ADD COLUMN IF NOT EXISTS stability_score FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS last_evolution TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trait_history_persona ON agent_trait_history(persona_id);
CREATE INDEX IF NOT EXISTS idx_trait_history_session ON agent_trait_history(session_id);
CREATE INDEX IF NOT EXISTS idx_trait_history_trait ON agent_trait_history(trait);
CREATE INDEX IF NOT EXISTS idx_trait_history_timestamp ON agent_trait_history(timestamp);

-- Function to calculate trait velocity (how fast traits are changing)
CREATE OR REPLACE FUNCTION calculate_trait_velocity(target_persona_id UUID, days_back INTEGER DEFAULT 7)
RETURNS TABLE(trait TEXT, velocity FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        th.trait,
        SUM(ABS(th.delta)) as velocity
    FROM agent_trait_history th
    WHERE th.persona_id = target_persona_id
      AND th.timestamp > NOW() - (days_back || ' days')::INTERVAL
    GROUP BY th.trait
    ORDER BY velocity DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get trait evolution summary
CREATE OR REPLACE FUNCTION get_trait_evolution_summary(target_persona_id UUID)
RETURNS TABLE(
    trait TEXT, 
    current_value FLOAT, 
    initial_value FLOAT,
    total_change FLOAT,
    change_events INTEGER,
    last_change TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    WITH trait_stats AS (
        SELECT 
            th.trait,
            COUNT(*) as change_events,
            MAX(th.timestamp) as last_change,
            FIRST_VALUE(th.value_before) OVER (PARTITION BY th.trait ORDER BY th.timestamp ASC) as initial_value,
            LAST_VALUE(th.value_after) OVER (PARTITION BY th.trait ORDER BY th.timestamp ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as current_value
        FROM agent_trait_history th
        WHERE th.persona_id = target_persona_id
        GROUP BY th.trait, th.value_before, th.value_after, th.timestamp
    )
    SELECT DISTINCT
        ts.trait,
        ts.current_value,
        ts.initial_value,
        (ts.current_value - ts.initial_value) as total_change,
        ts.change_events,
        ts.last_change
    FROM trait_stats ts
    ORDER BY ABS(ts.current_value - ts.initial_value) DESC;
END;
$$ LANGUAGE plpgsql;

-- Insert sample trait history for testing (will be replaced by real data)
-- This helps verify the schema works correctly
INSERT INTO agent_trait_history (persona_id, session_id, trait, value_before, value_after, delta, source_event)
SELECT 
    p.id as persona_id,
    'schema-test-session' as session_id,
    'extraversion' as trait,
    0.5 as value_before,
    0.52 as value_after,
    0.02 as delta,
    'schema_test' as source_event
FROM persona_profiles p
WHERE p.name = 'Kai the Coach'
LIMIT 1;

-- Clean up test data
DELETE FROM agent_trait_history WHERE source_event = 'schema_test';
