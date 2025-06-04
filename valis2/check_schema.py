#!/usr/bin/env python3
"""
Quick schema check for VALIS database
"""
import sys
from pathlib import Path

# Add valis2 to path
valis2_dir = Path(__file__).parent
sys.path.append(str(valis2_dir))

from memory.db import db

try:
    # Check persona_profiles columns
    result = db.query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'persona_profiles'
        ORDER BY ordinal_position
    """)
    
    print("persona_profiles columns:")
    for row in result:
        print(f"  {row['column_name']}: {row['data_type']}")
    
    # Check if any personas exist
    personas = db.query("SELECT * FROM persona_profiles LIMIT 1")
    if personas:
        print(f"\nSample persona columns: {list(personas[0].keys())}")
    else:
        print("\nNo personas found in database")
        
except Exception as e:
    print(f"Error: {e}")
