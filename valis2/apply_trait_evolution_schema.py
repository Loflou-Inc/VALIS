#!/usr/bin/env python3
"""
Apply Trait Evolution Schema to VALIS Database
Sprint 13: Persona Evolution & Adaptive Dialogue
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def apply_trait_evolution_schema():
    """Apply the trait evolution schema to the database"""
    print("Applying Trait Evolution Schema...")
    
    try:
        with open('db/schema_trait_evolution_simple.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split into individual statements and execute each
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                print(f"Executing statement {i+1}/{len(statements)}...")
                db.execute(statement)
        
        print("[+] Trait Evolution schema applied successfully")
        
        # Verify tables were created
        tables = db.query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%trait%'
            ORDER BY table_name
        """)
        
        print(f"[+] Found {len(tables)} trait-related tables:")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # Check if new columns were added
        columns = db.query("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'agent_personality_profiles'
            AND column_name IN ('evolving_traits', 'evolution_rate', 'stability_score')
        """)
        
        print(f"[+] Added {len(columns)} new columns to personality profiles:")
        for col in columns:
            print(f"    - {col['column_name']}")
        
        return True
        
    except Exception as e:
        print(f"[-] Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_trait_evolution_schema()
    if not success:
        sys.exit(1)
