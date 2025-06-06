-- VALIS Sprint 14: DreamFilter Schema (Simplified)
-- Unconscious symbolic expression and dream logging

-- Unconscious log for storing agent dreams and symbolic content
CREATE TABLE IF NOT EXISTS unconscious_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    dream_type TEXT NOT NULL,  -- poem, vision, dialogue, nightmare, memory_fragment
    content TEXT NOT NULL,
    source_summary JSONB,  -- metadata about memory/emotion sources
    symbolic_weight FLOAT DEFAULT 1.0,  -- how symbolic vs literal the content is
    emotional_resonance FLOAT DEFAULT 0.5,  -- how emotionally charged
    archetype_tags JSONB DEFAULT '[]',  -- jungian archetypes present
    session_trigger TEXT,  -- what triggered this dream
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Dream scheduling and trigger tracking
CREATE TABLE IF NOT EXISTS dream_schedule (
    agent_id UUID PRIMARY KEY,
    last_dream_time TIMESTAMP,
    next_dream_due TIMESTAMP,
    dream_frequency_hours INTEGER DEFAULT 6,  -- how often agent dreams
    idle_threshold_minutes INTEGER DEFAULT 3,  -- idle time before dreaming
    dream_enabled BOOLEAN DEFAULT TRUE,
    consecutive_dreams INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Dream pattern analysis (for future sprint expansion)
CREATE TABLE IF NOT EXISTS dream_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    pattern_type TEXT NOT NULL,  -- recurring_symbol, emotional_theme, archetype_cycle
    pattern_description TEXT,
    occurrences INTEGER DEFAULT 1,
    first_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_unconscious_log_agent ON unconscious_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_unconscious_log_timestamp ON unconscious_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_unconscious_log_dream_type ON unconscious_log(dream_type);
CREATE INDEX IF NOT EXISTS idx_dream_schedule_next_due ON dream_schedule(next_dream_due);
CREATE INDEX IF NOT EXISTS idx_dream_patterns_agent ON dream_patterns(agent_id);
