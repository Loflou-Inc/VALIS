# VALIS 2.0 Sprint 2 Setup Guide

## Database Setup Options

### Option A: PostgreSQL (Production)
1. Install PostgreSQL: https://www.postgresql.org/download/windows/
2. Create database: `createdb valis2`
3. Create user: `createuser -P valis` (password: valis123)
4. Grant access: `GRANT ALL PRIVILEGES ON DATABASE valis2 TO valis;`

### Option B: SQLite (Development/Testing)
No setup required - uses local file database

## Installation & Testing

```bash
# Install Python dependencies
pip install psycopg2-binary

# Initialize database (PostgreSQL)
cd C:\VALIS\valis2
python memory\init_db.py

# OR use SQLite fallback
python memory\init_db_sqlite.py

# Test integration
python test_db_integration.py
```

## Sprint 2 Deliverables

✅ SQL Schema (schema.sql)
✅ Database Client (db.py) 
✅ Memory Query Layer (query_client.py)
✅ MCPRuntime Integration (updated mcp_runtime.py)
✅ Seeder Script (seed_data.py)
✅ Integration Test (test_db_integration.py)

## Next Steps

- Install PostgreSQL for production
- Run database initialization
- Test memory-backed inference
- Move to Sprint 3: Persona-Aware Routing
