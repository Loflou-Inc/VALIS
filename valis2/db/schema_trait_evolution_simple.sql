-- VALIS Sprint 13: Trait History and Evolution Schema (Simplified)
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
ADD COLUMN IF NOT EXISTS evolution_rate FLOAT DEFAULT 0.1;

ALTER TABLE agent_personality_profiles
ADD COLUMN IF NOT EXISTS stability_score FLOAT DEFAULT 1.0;

ALTER TABLE agent_personality_profiles
ADD COLUMN IF NOT EXISTS last_evolution TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trait_history_persona ON agent_trait_history(persona_id);
CREATE INDEX IF NOT EXISTS idx_trait_history_session ON agent_trait_history(session_id);
CREATE INDEX IF NOT EXISTS idx_trait_history_trait ON agent_trait_history(trait);
CREATE INDEX IF NOT EXISTS idx_trait_history_timestamp ON agent_trait_history(timestamp);
