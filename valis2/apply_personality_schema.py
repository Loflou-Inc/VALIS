#!/usr/bin/env python3
"""
Apply Personality Engine Schema to VALIS Database
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_personality_schema():
    """Apply the personality engine schema to the database"""
    print("Applying Personality Engine Schema...")
    
    try:
        with open('db/schema_personality_engine.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split into individual statements and execute each
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                print(f"Executing statement {i+1}/{len(statements)}...")
                db.execute(statement)
        
        print("[+] Personality Engine schema applied successfully")
        
        # Verify tables were created
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%personality%'
            ORDER BY table_name
        """)
        
        print(f"[+] Created {len(tables)} personality tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_personality_schema()
    if not success:
        sys.exit(1)
