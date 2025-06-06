import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'valis2'))

from memory.db import db

# Check for specific mortality-related tables using the PostgreSQL database
target_tables = [
    'agent_mortality',
    'agent_legacy_score', 
    'agent_lineage',
    'agent_final_thoughts',
    'mortality_statistics'
]

try:
    # Get all tables from PostgreSQL
    all_tables = db.query("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    table_names = [table['table_name'] for table in all_tables]
    
    print("All tables in database:")
    for table in table_names:
        print(f"  - {table}")

    print("\nMortality-related tables:")
    found_tables = [t for t in table_names if any(target in t for target in ['mortality', 'legacy', 'lineage', 'final_thoughts'])]

    if found_tables:
        for table in found_tables:
            print(f"  - {table}")
            
        # Also show record counts
        print("\nRecord counts:")
        for table in found_tables:
            try:
                count = db.query(f"SELECT COUNT(*) as count FROM {table}")[0]['count']
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error getting count - {e}")
    else:
        print("  No mortality tables found")
        
except Exception as e:
    print(f"Error connecting to database: {e}")
