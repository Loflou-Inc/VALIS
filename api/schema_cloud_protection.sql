-- VALIS Phase 4: Cloud Soul & Containment Protocols
-- Database schema for API protection, authentication, and usage tracking

-- API Keys for authentication and access control
CREATE TABLE IF NOT EXISTS valis_api_keys (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key TEXT UNIQUE NOT NULL,
    key_name TEXT NOT NULL,
    key_description TEXT,
    usage_limit INTEGER DEFAULT 1000,
    usage_count INTEGER DEFAULT 0,
    permissions TEXT[] DEFAULT ARRAY['persona_create', 'persona_chat', 'persona_status'],
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_by TEXT DEFAULT 'system'
);

-- API Usage Logging for protection and analytics
CREATE TABLE IF NOT EXISTS valis_api_usage_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    persona_id UUID,
    session_id UUID,
    endpoint TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    api_key_hash TEXT,
    usage_type TEXT DEFAULT 'standard',
    response_size INTEGER,
    processing_time_ms INTEGER,
    error_code INTEGER,
    symbolic_signature TEXT,
    valis_trace TEXT,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE SET NULL
);

-- VALIS Output Watermarks for traceability
CREATE TABLE IF NOT EXISTS valis_output_watermarks (
    watermark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    valis_trace TEXT UNIQUE NOT NULL,
    persona_id UUID NOT NULL,
    session_id UUID NOT NULL,
    request_id UUID NOT NULL,
    symbolic_signature TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT,
    protection_level TEXT DEFAULT 'standard',
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Persona Session Tracking for continuity
CREATE TABLE IF NOT EXISTS valis_persona_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID NOT NULL,
    api_key_hash TEXT,
    session_start TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMPTZ,
    interaction_count INTEGER DEFAULT 0,
    total_symbolic_weight FLOAT DEFAULT 0.0,
    session_summary TEXT,
    consolidation_triggered BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- VALIS System Metrics for monitoring
CREATE TABLE IF NOT EXISTS valis_system_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type TEXT DEFAULT 'counter',
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    persona_id UUID,
    additional_data JSONB DEFAULT '{}',
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE SET NULL
);

-- Performance indexes for API operations
CREATE INDEX IF NOT EXISTS idx_api_usage_log_timestamp ON valis_api_usage_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_log_persona ON valis_api_usage_log(persona_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_log_endpoint ON valis_api_usage_log(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_log_api_key ON valis_api_usage_log(api_key_hash);

CREATE INDEX IF NOT EXISTS idx_watermarks_trace ON valis_output_watermarks(valis_trace);
CREATE INDEX IF NOT EXISTS idx_watermarks_persona ON valis_output_watermarks(persona_id);
CREATE INDEX IF NOT EXISTS idx_watermarks_timestamp ON valis_output_watermarks(timestamp);

CREATE INDEX IF NOT EXISTS idx_persona_sessions_id ON valis_persona_sessions(persona_id);
CREATE INDEX IF NOT EXISTS idx_persona_sessions_start ON valis_persona_sessions(session_start);

CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON valis_system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON valis_system_metrics(timestamp);

-- Seed initial API key for demo/testing
INSERT INTO valis_api_keys (api_key, key_name, key_description, usage_limit, permissions) 
VALUES (
    'valis_demo_consciousness_api_4_0',
    'Demo Key',
    'Demonstration access to VALIS Synthetic Consciousness API',
    100,
    ARRAY['persona_create', 'persona_chat', 'persona_status']
) ON CONFLICT (api_key) DO NOTHING;

-- Seed additional development key
INSERT INTO valis_api_keys (api_key, key_name, key_description, usage_limit, permissions)
VALUES (
    'valis_dev_soul_awake_key_2025',
    'Development Key',
    'Development access for VALIS Phase 4 testing',
    1000,
    ARRAY['persona_create', 'persona_chat', 'persona_status', 'admin_access']
) ON CONFLICT (api_key) DO NOTHING;
