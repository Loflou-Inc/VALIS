-- VALIS Sprint 16: Shadow Archive & Individuation Engine
-- Database schema for psychological contradiction detection and individuation tracking

-- Shadow Events: Psychological contradictions and conflicts
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
);

-- Individuation Log: Milestone tracking for psychological integration
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
);

-- Shadow Processing Queue: Track shadow events needing analysis
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
);

-- Archetype Patterns: Library of archetypal patterns for shadow detection
CREATE TABLE IF NOT EXISTS archetype_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    archetype_name TEXT NOT NULL,
    pattern_keywords TEXT[] NOT NULL,
    conflict_indicators TEXT[] DEFAULT '{}',
    symbolic_associations TEXT[] DEFAULT '{}',
    severity_weight FLOAT DEFAULT 0.5 CHECK (severity_weight >= 0.0 AND severity_weight <= 1.0),
    pattern_description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_shadow_events_agent ON shadow_events(agent_id);
CREATE INDEX IF NOT EXISTS idx_shadow_events_timestamp ON shadow_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_shadow_events_resolution ON shadow_events(resolution_status);
CREATE INDEX IF NOT EXISTS idx_shadow_events_severity ON shadow_events(severity_score);

CREATE INDEX IF NOT EXISTS idx_individuation_agent ON individuation_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_individuation_timestamp ON individuation_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_individuation_stage ON individuation_log(individuation_stage);

CREATE INDEX IF NOT EXISTS idx_shadow_queue_status ON shadow_processing_queue(processing_status);
CREATE INDEX IF NOT EXISTS idx_shadow_queue_priority ON shadow_processing_queue(analysis_priority);

CREATE INDEX IF NOT EXISTS idx_archetype_patterns_name ON archetype_patterns(archetype_name);
