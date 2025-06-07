-- VALIS 2.0 Execution Logging Schema Extension
-- Add execution audit table for Desktop Commander integration

-- Execution logs for command tracking and audit
CREATE TABLE IF NOT EXISTS execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(8) NOT NULL,
    client_id UUID REFERENCES client_profiles(id) ON DELETE CASCADE,
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    intent VARCHAR(50) NOT NULL,
    function_name VARCHAR(100) NOT NULL,
    parameters JSONB,
    command_text TEXT,
    success BOOLEAN NOT NULL,
    result_preview TEXT,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for execution logs
CREATE INDEX IF NOT EXISTS idx_execution_logs_client_id ON execution_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_intent ON execution_logs(intent);
CREATE INDEX IF NOT EXISTS idx_execution_logs_created_at ON execution_logs(created_at DESC);

-- Command allowlist table for security
CREATE TABLE IF NOT EXISTS command_allowlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
    command_pattern VARCHAR(255) NOT NULL,
    allowed BOOLEAN DEFAULT true,
    risk_level VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default command allowlist
INSERT INTO command_allowlist (persona_id, command_pattern, allowed, risk_level) 
SELECT id, 'list_files', true, 'low' FROM persona_profiles
ON CONFLICT DO NOTHING;

INSERT INTO command_allowlist (persona_id, command_pattern, allowed, risk_level)
SELECT id, 'read_file', true, 'low' FROM persona_profiles  
ON CONFLICT DO NOTHING;

INSERT INTO command_allowlist (persona_id, command_pattern, allowed, risk_level)
SELECT id, 'search_files', true, 'low' FROM persona_profiles
ON CONFLICT DO NOTHING;

INSERT INTO command_allowlist (persona_id, command_pattern, allowed, risk_level)
SELECT id, 'execute_command', false, 'high' FROM persona_profiles
ON CONFLICT DO NOTHING;
