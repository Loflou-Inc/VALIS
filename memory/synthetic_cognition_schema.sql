-- VALIS 2.0 Synthetic Cognition Layer Schema
-- PostgreSQL schema for agent self-model, emotion states, and reflection

-- Drop tables if they exist (for clean reinitialization)
DROP TABLE IF EXISTS canon_memory_emotion_map CASCADE;
DROP TABLE IF EXISTS agent_reflection_log CASCADE;
DROP TABLE IF EXISTS agent_emotion_state CASCADE;
DROP TABLE IF EXISTS agent_self_profiles CASCADE;

-- Agent self-awareness and ego state tracking
CREATE TABLE agent_self_profiles (
    persona_id UUID PRIMARY KEY REFERENCES persona_profiles(id) ON DELETE CASCADE,
    traits JSONB NOT NULL DEFAULT '{}',
    last_alignment_score FLOAT DEFAULT 0.5,
    working_self_state JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent emotional state per session
CREATE TABLE agent_emotion_state (
    session_id TEXT PRIMARY KEY,
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    mood TEXT DEFAULT 'neutral',
    arousal_level INTEGER DEFAULT 5 CHECK (arousal_level >= 1 AND arousal_level <= 10),
    emotion_tags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent reflection and metacognitive logs
CREATE TABLE agent_reflection_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    reflection TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    plan_success_score FLOAT,
    ego_alignment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emotional tagging of canonical memories
CREATE TABLE canon_memory_emotion_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID REFERENCES canon_memories(id) ON DELETE CASCADE,
    emotion_tag TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    source TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_agent_self_profiles_persona ON agent_self_profiles(persona_id);
CREATE INDEX idx_agent_self_profiles_alignment ON agent_self_profiles(last_alignment_score DESC);

CREATE INDEX idx_agent_emotion_state_persona ON agent_emotion_state(persona_id);
CREATE INDEX idx_agent_emotion_state_session ON agent_emotion_state(session_id);
CREATE INDEX idx_agent_emotion_state_mood ON agent_emotion_state(mood);

CREATE INDEX idx_agent_reflection_log_persona ON agent_reflection_log(persona_id);
CREATE INDEX idx_agent_reflection_log_session ON agent_reflection_log(session_id);
CREATE INDEX idx_agent_reflection_log_created ON agent_reflection_log(created_at DESC);

CREATE INDEX idx_canon_memory_emotion_memory ON canon_memory_emotion_map(memory_id);
CREATE INDEX idx_canon_memory_emotion_tag ON canon_memory_emotion_map(emotion_tag);
CREATE INDEX idx_canon_memory_emotion_weight ON canon_memory_emotion_map(weight DESC);

-- Update timestamp triggers
CREATE TRIGGER update_agent_self_profiles_updated_at BEFORE UPDATE ON agent_self_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_emotion_state_updated_at BEFORE UPDATE ON agent_emotion_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE agent_self_profiles IS 'Persistent ego state and trait alignment tracking per persona';
COMMENT ON TABLE agent_emotion_state IS 'Emotional state tracking per session with mood and arousal levels';
COMMENT ON TABLE agent_reflection_log IS 'Metacognitive reflection logs for plan analysis and self-evaluation';
COMMENT ON TABLE canon_memory_emotion_map IS 'Emotional weighting and tagging of canonical memories';
