#!/usr/bin/env python3
"""
Apply Enhanced Logging Schema - Sprint 9 Carryover
"""
import sys
from pathlib import Path

# Add valis2 to path
sys.path.append(str(Path(__file__).parent))

from memory.db import db

def apply_enhanced_logging_schema():
    """Apply the enhanced logging schema"""
    
    schema_sql = """
    -- Enhanced Logging Schema for Sprint 9 Carryover
    ALTER TABLE session_logs 
    ADD COLUMN IF NOT EXISTS request_id VARCHAR(8),
    ADD COLUMN IF NOT EXISTS provider_used VARCHAR(50),
    ADD COLUMN IF NOT EXISTS processing_time FLOAT,
    ADD COLUMN IF NOT EXISTS tool_calls_made INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS autonomous_plan_id VARCHAR(8),
    ADD COLUMN IF NOT EXISTS metadata_json JSONB;

    CREATE TABLE IF NOT EXISTS session_correlations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_log_id UUID REFERENCES session_logs(id) ON DELETE CASCADE,
        request_id VARCHAR(8),
        correlation_type VARCHAR(30) NOT NULL CHECK (correlation_type IN ('tool_execution', 'autonomous_execution', 'memory_query')),
        plan_id VARCHAR(8),
        execution_id VARCHAR(8),
        tool_name VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_session_correlations_session ON session_correlations(session_log_id);
    CREATE INDEX IF NOT EXISTS idx_session_correlations_request ON session_correlations(request_id);
    CREATE INDEX IF NOT EXISTS idx_session_correlations_type ON session_correlations(correlation_type);
    CREATE INDEX IF NOT EXISTS idx_session_correlations_plan ON session_correlations(plan_id);

    ALTER TABLE execution_logs 
    ADD COLUMN IF NOT EXISTS request_id VARCHAR(8);

    CREATE INDEX IF NOT EXISTS idx_execution_logs_request ON execution_logs(request_id);
    """
    
    try:
        print("Applying enhanced logging schema...")
        db.execute(schema_sql)
        print("SUCCESS: Enhanced logging schema applied successfully")
        
    except Exception as e:
        print(f"ERROR: Failed to apply enhanced logging schema: {e}")
        raise

if __name__ == "__main__":
    apply_enhanced_logging_schema()
