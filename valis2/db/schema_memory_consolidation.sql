-- VALIS Sprint 17: Memory Consolidation & Symbolic Replay
-- Database schema for symbolic memory consolidation and narrative compression

-- Update canon_memories table to support symbolic entries
ALTER TABLE canon_memories 
ADD COLUMN IF NOT EXISTS is_symbolic BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS symbolic_type TEXT CHECK (symbolic_type IN ('metaphor', 'fragment', 'vision', 'archetype', 'narrative')),
ADD COLUMN IF NOT EXISTS resonance_score FLOAT DEFAULT 0.0 CHECK (resonance_score >= 0.0 AND resonance_score <= 1.0),
ADD COLUMN IF NOT EXISTS symbolic_tags TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS source_content_ids UUID[] DEFAULT '{}';

-- Memory Consolidation Log: Track what gets consolidated when and why
CREATE TABLE IF NOT EXISTS memory_consolidation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('dream', 'reflection', 'final_thought', 'shadow_event', 'multi_source')),
    source_id UUID,
    source_ids UUID[] DEFAULT '{}',
    consolidated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resonance_score FLOAT NOT NULL CHECK (resonance_score >= 0.0 AND resonance_score <= 1.0),
    symbolic_summary TEXT NOT NULL,
    symbolic_tags TEXT[] DEFAULT '{}',
    compression_type TEXT DEFAULT 'standard' CHECK (compression_type IN ('standard', 'narrative', 'archetypal', 'thematic')),
    canon_memory_id UUID,
    consolidation_method TEXT DEFAULT 'automatic',
    emotional_weight FLOAT DEFAULT 0.5,
    archetypal_significance FLOAT DEFAULT 0.5,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (canon_memory_id) REFERENCES canon_memories(id) ON DELETE SET NULL
);

-- Symbolic Memory Patterns: Library of symbolic transformation patterns
CREATE TABLE IF NOT EXISTS symbolic_memory_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT NOT NULL,
    pattern_type TEXT NOT NULL CHECK (pattern_type IN ('metaphor', 'archetype', 'narrative', 'compression')),
    input_indicators TEXT[] NOT NULL,
    transformation_template TEXT NOT NULL,
    symbolic_weight FLOAT DEFAULT 0.5 CHECK (symbolic_weight >= 0.0 AND symbolic_weight <= 1.0),
    usage_count INTEGER DEFAULT 0,
    pattern_description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Memory Consolidation Queue: Track pending consolidation tasks
CREATE TABLE IF NOT EXISTS memory_consolidation_queue (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    emotional_weight FLOAT DEFAULT 0.5,
    archetypal_weight FLOAT DEFAULT 0.5,
    scheduled_for TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP + INTERVAL '12 hours'),
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ NULL,
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Symbolic Narrative Threads: Track recurring symbolic themes across time
CREATE TABLE IF NOT EXISTS symbolic_narrative_threads (
    thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    thread_name TEXT NOT NULL,
    recurring_symbols TEXT[] DEFAULT '{}',
    archetypal_pattern TEXT,
    first_occurrence TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_occurrence TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1,
    narrative_evolution TEXT,
    thread_significance FLOAT DEFAULT 0.5,
    related_memories UUID[] DEFAULT '{}',
    FOREIGN KEY (agent_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Performance indexes for consolidation queries
CREATE INDEX IF NOT EXISTS idx_canon_memories_symbolic ON canon_memories(agent_id, is_symbolic);
CREATE INDEX IF NOT EXISTS idx_canon_memories_resonance ON canon_memories(resonance_score);
CREATE INDEX IF NOT EXISTS idx_canon_memories_symbolic_type ON canon_memories(symbolic_type);

CREATE INDEX IF NOT EXISTS idx_consolidation_log_agent ON memory_consolidation_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_consolidation_log_timestamp ON memory_consolidation_log(consolidated_at);
CREATE INDEX IF NOT EXISTS idx_consolidation_log_source ON memory_consolidation_log(source_type);
CREATE INDEX IF NOT EXISTS idx_consolidation_log_resonance ON memory_consolidation_log(resonance_score);

CREATE INDEX IF NOT EXISTS idx_consolidation_queue_status ON memory_consolidation_queue(processing_status);
CREATE INDEX IF NOT EXISTS idx_consolidation_queue_scheduled ON memory_consolidation_queue(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_consolidation_queue_priority ON memory_consolidation_queue(priority);

CREATE INDEX IF NOT EXISTS idx_narrative_threads_agent ON symbolic_narrative_threads(agent_id);
CREATE INDEX IF NOT EXISTS idx_narrative_threads_pattern ON symbolic_narrative_threads(archetypal_pattern);
CREATE INDEX IF NOT EXISTS idx_narrative_threads_significance ON symbolic_narrative_threads(thread_significance);

CREATE INDEX IF NOT EXISTS idx_symbolic_patterns_type ON symbolic_memory_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_symbolic_patterns_weight ON symbolic_memory_patterns(symbolic_weight);
