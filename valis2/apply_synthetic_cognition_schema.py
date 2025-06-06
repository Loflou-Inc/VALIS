#!/usr/bin/env python3
"""
Apply Synthetic Cognition Schema - Sprint 11
Add database tables for agent self-model, emotion states, and reflection
"""
import sys
from pathlib import Path

# Add valis2 to path
sys.path.append(str(Path(__file__).parent))

from memory.db import db

def apply_synthetic_cognition_schema():
    """Apply the synthetic cognition database schema"""
    
    # Read the schema file
    schema_path = Path(__file__).parent / "memory" / "synthetic_cognition_schema.sql"
    
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        print("Applying synthetic cognition schema...")
        db.execute(schema_sql)
        print("SUCCESS: Synthetic cognition schema applied successfully")
        
        # Verify tables were created
        result = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'agent_%'
        """)
        
        created_tables = [row['table_name'] for row in result]
        print(f"SUCCESS: Created/verified tables: {created_tables}")
        
        expected_tables = ['agent_self_profiles', 'agent_emotion_state', 'agent_reflection_log']
        for table in expected_tables:
            if table in created_tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [MISSING] {table}")
                
        # Check canon_memory_emotion_map separately
        result = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'canon_memory_emotion_map'
        """)
        
        if result:
            print(f"  [OK] canon_memory_emotion_map")
        else:
            print(f"  [MISSING] canon_memory_emotion_map")
        
    except Exception as e:
        print(f"ERROR: Failed to apply schema: {e}")
        raise

if __name__ == "__main__":
    apply_synthetic_cognition_schema()
