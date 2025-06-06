#!/usr/bin/env python3
"""
Apply Agent Plans Schema - Sprint 10
Add database tables for autonomous planning
"""
import sys
from pathlib import Path

# Add valis2 to path
sys.path.append(str(Path(__file__).parent))

from memory.db import db

def apply_agent_plans_schema():
    """Apply the agent plans database schema"""
    
    schema_sql = """
    -- Agent Plans Table for Sprint 10
    CREATE TABLE IF NOT EXISTS agent_plans (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        plan_id VARCHAR(8) UNIQUE NOT NULL,
        client_id UUID NOT NULL REFERENCES client_profiles(id) ON DELETE CASCADE,
        persona_id UUID NOT NULL REFERENCES persona_profiles(id) ON DELETE CASCADE,
        goal TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'planning' CHECK (status IN ('planning', 'executing', 'completed', 'failed', 'cancelled')),
        plan_data JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        completed_at TIMESTAMP WITH TIME ZONE,
        execution_time FLOAT,
        step_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_agent_plans_client ON agent_plans(client_id);
    CREATE INDEX IF NOT EXISTS idx_agent_plans_persona ON agent_plans(persona_id);
    CREATE INDEX IF NOT EXISTS idx_agent_plans_status ON agent_plans(status);
    CREATE INDEX IF NOT EXISTS idx_agent_plans_created ON agent_plans(created_at DESC);

    CREATE TABLE IF NOT EXISTS agent_plan_steps (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        plan_id VARCHAR(8) NOT NULL,
        step_id VARCHAR(10) NOT NULL,
        step_type VARCHAR(20) NOT NULL,
        tool_name VARCHAR(50),
        status VARCHAR(20) DEFAULT 'pending',
        parameters JSONB,
        result JSONB,
        error TEXT,
        execution_time FLOAT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        executed_at TIMESTAMP WITH TIME ZONE,
        FOREIGN KEY (plan_id) REFERENCES agent_plans(plan_id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_plan_steps_plan ON agent_plan_steps(plan_id);
    CREATE INDEX IF NOT EXISTS idx_plan_steps_status ON agent_plan_steps(status);
    """
    
    try:
        print("Applying agent plans schema...")
        db.execute(schema_sql)
        print("SUCCESS: Agent plans schema applied successfully")
        
        # Verify tables were created
        result = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'agent_plan%'
        """)
        
        print(f"SUCCESS: Created tables: {[row['table_name'] for row in result]}")
        
    except Exception as e:
        print(f"ERROR: Failed to apply schema: {e}")
        raise

if __name__ == "__main__":
    apply_agent_plans_schema()
