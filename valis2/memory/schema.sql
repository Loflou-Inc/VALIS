-- VALIS 2.0 Memory Spine Schema
-- PostgreSQL schema for persistent, persona-scoped memory

-- Drop tables if they exist (for clean reinitialization)
DROP TABLE IF EXISTS session_logs CASCADE;
DROP TABLE IF EXISTS working_memory CASCADE;
DROP TABLE IF EXISTS canon_memories CASCADE;
DROP TABLE IF EXISTS client_profiles CASCADE;
DROP TABLE IF EXISTS persona_profiles CASCADE;

-- Core persona definitions
CREATE TABLE persona_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT,
    bio TEXT,
    system_prompt TEXT,
    traits JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client/user profiles
CREATE TABLE client_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    email TEXT,
    traits JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Long-term canonical facts/knowledge per persona
CREATE TABLE canon_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    tags TEXT[],
    category TEXT,
    relevance_score FLOAT DEFAULT 1.0,
    token_estimate INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Short-term working memory with decay
CREATE TABLE working_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    client_id UUID REFERENCES client_profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    importance INTEGER DEFAULT 5,
    decay_score FLOAT DEFAULT 1.0,
    expires_at TIMESTAMP,
    token_estimate INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Session dialogue logs
CREATE TABLE session_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    client_id UUID REFERENCES client_profiles(id) ON DELETE CASCADE,
    session_id TEXT,
    turn_index INTEGER,
    user_input TEXT,
    assistant_reply TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_canon_memories_persona_id ON canon_memories(persona_id);
CREATE INDEX idx_canon_memories_relevance ON canon_memories(relevance_score DESC);
CREATE INDEX idx_canon_memories_last_used ON canon_memories(last_used DESC);

CREATE INDEX idx_working_memory_persona_client ON working_memory(persona_id, client_id);
CREATE INDEX idx_working_memory_decay_score ON working_memory(decay_score DESC);
CREATE INDEX idx_working_memory_expires_at ON working_memory(expires_at);

CREATE INDEX idx_session_logs_persona_client ON session_logs(persona_id, client_id);
CREATE INDEX idx_session_logs_session_id ON session_logs(session_id);
CREATE INDEX idx_session_logs_created_at ON session_logs(created_at DESC);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_persona_profiles_updated_at BEFORE UPDATE ON persona_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
