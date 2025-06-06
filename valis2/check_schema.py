#!/usr/bin/env python3
"""
Check agent_self_profiles schema
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def check_schema():
    try:
        # Check working_memory table
        wm_columns = db.query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'working_memory'
        """)
        
        print("working_memory columns:")
        for col in wm_columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
            
        # Check canon_memories table
        cm_columns = db.query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'canon_memories'
        """)
        
        print("\ncanon_memories columns:")
        for col in cm_columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
