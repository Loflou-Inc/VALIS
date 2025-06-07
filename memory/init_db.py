"""
VALIS 2.0 Database Initialization
Setup PostgreSQL schema and seed data
"""
import os
import sys
import psycopg2
from pathlib import Path

import os
import sys
import psycopg2
from pathlib import Path

# Add valis2 directory to path
valis2_dir = Path(__file__).parent.parent
sys.path.append(str(valis2_dir))

from memory.db import db

def init_database():
    """Initialize database schema"""
    print("DB Initializing VALIS 2.0 database schema...")
    
    # Read schema file
    schema_file = Path(__file__).parent / "schema.sql"
    
    if not schema_file.exists():
        print("ERROR Schema file not found!")
        return False
    
    schema_sql = schema_file.read_text()
    
    try:
        # Execute schema
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                conn.commit()
        
        print("OK Database schema initialized successfully")
        return True
        
    except Exception as e:
        print(f"ERROR Failed to initialize database: {e}")
        return False

def seed_database():
    """Seed database with sample data"""
    print("SEED Seeding database with sample data...")
    
    try:
        from memory.seed_data import run_seeder
        run_seeder()
        return True
    except Exception as e:
        print(f"ERROR Failed to seed database: {e}")
        return False

def main():
    """Main initialization routine"""
    print("=== VALIS 2.0 Database Setup ===")
    
    # Check database connection
    try:
        db.query("SELECT 1")
        print("OK Database connection successful")
    except Exception as e:
        print(f"ERROR Database connection failed: {e}")
        print("Make sure PostgreSQL is running and credentials are correct in .env")
        return
    
    # Initialize schema
    if not init_database():
        return
    
    # Seed data
    if not seed_database():
        return
    
    print("SUCCESS VALIS 2.0 database setup complete!")

if __name__ == "__main__":
    main()
