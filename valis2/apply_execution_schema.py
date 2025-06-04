#!/usr/bin/env python3
"""
Apply execution schema to VALIS database
"""
import sys
from pathlib import Path

# Add valis2 to path
valis2_dir = Path(__file__).parent
sys.path.append(str(valis2_dir))

from memory.db import db

def apply_execution_schema():
    """Apply execution logging schema to database"""
    
    # Create execution_logs table
    db.execute("""
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
        )
    """)
    
    # Create indexes
    db.execute("CREATE INDEX IF NOT EXISTS idx_execution_logs_client_id ON execution_logs(client_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id ON execution_logs(execution_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_execution_logs_intent ON execution_logs(intent)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_execution_logs_created_at ON execution_logs(created_at DESC)")
    
    # Create command allowlist table
    db.execute("""
        CREATE TABLE IF NOT EXISTS command_allowlist (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            persona_id UUID REFERENCES persona_profiles(id) ON DELETE CASCADE,
            command_pattern VARCHAR(255) NOT NULL,
            allowed BOOLEAN DEFAULT true,
            risk_level VARCHAR(20) DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print(">> Execution schema applied successfully")

if __name__ == "__main__":
    apply_execution_schema()
