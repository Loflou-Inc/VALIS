-- Agent Plans Table for Sprint 10
-- Stores autonomous multi-step plans created by VALIS agents

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

-- Index for efficient queries
CREATE INDEX IF NOT EXISTS idx_agent_plans_client ON agent_plans(client_id);
CREATE INDEX IF NOT EXISTS idx_agent_plans_persona ON agent_plans(persona_id);
CREATE INDEX IF NOT EXISTS idx_agent_plans_status ON agent_plans(status);
CREATE INDEX IF NOT EXISTS idx_agent_plans_created ON agent_plans(created_at DESC);

-- Plan Steps Table (optional - could be stored in JSONB instead)
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
