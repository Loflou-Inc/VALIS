#!/usr/bin/env python3
"""
Check existing personas in VALIS database
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

def check_personas():
    """List all personas in the database"""
    try:
        personas = db.query("SELECT id, name, role, bio FROM persona_profiles ORDER BY name")
        
        if personas:
            print(f"Found {len(personas)} personas in database:")
            for persona in personas:
                print(f"  - {persona['name']} (ID: {persona['id']}) - {persona['role']}")
        else:
            print("No personas found in database")
            
        return personas
        
    except Exception as e:
        print(f"Error checking personas: {e}")
        return []

if __name__ == "__main__":
    check_personas()
