-- Enhanced Logging Schema for Sprint 9 Carryover
-- Adds correlation tracking between sessions, tools, and autonomous plans

-- Update session_logs table to include enhanced fields
ALTER TABLE session_logs 
ADD COLUMN IF NOT EXISTS request_id VARCHAR(8),
ADD COLUMN IF NOT EXISTS provider_used VARCHAR(50),
ADD COLUMN IF NOT EXISTS processing_time FLOAT,
ADD COLUMN IF NOT EXISTS tool_calls_made INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS autonomous_plan_id VARCHAR(8),
ADD COLUMN IF NOT EXISTS metadata_json JSONB;

-- Create correlations table for linking sessions to other activities
CREATE TABLE IF NOT EXISTS session_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_log_id UUID REFERENCES session_logs(id) ON DELETE CASCADE,
    request_id VARCHAR(8),
    correlation_type VARCHAR(30) NOT NULL CHECK (correlation_type IN ('tool_execution', 'autonomous_execution', 'memory_query')),
    -- Flexible reference fields
    plan_id VARCHAR(8),
    execution_id VARCHAR(8),
    tool_name VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_correlations_session ON session_correlations(session_log_id);
CREATE INDEX IF NOT EXISTS idx_session_correlations_request ON session_correlations(request_id);
CREATE INDEX IF NOT EXISTS idx_session_correlations_type ON session_correlations(correlation_type);
CREATE INDEX IF NOT EXISTS idx_session_correlations_plan ON session_correlations(plan_id);

-- Update execution_logs table to include request_id if not exists
ALTER TABLE execution_logs 
ADD COLUMN IF NOT EXISTS request_id VARCHAR(8);

CREATE INDEX IF NOT EXISTS idx_execution_logs_request ON execution_logs(request_id);
