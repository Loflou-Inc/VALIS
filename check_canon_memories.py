import sys
sys.path.append('valis2')
from memory.db import db

# Check canon_memories schema
columns = db.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'canon_memories' ORDER BY ordinal_position")
print('canon_memories schema:')
for col in columns:
    print(f'  {col["column_name"]}: {col["data_type"]}')

# Check if table exists
tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_name = 'canon_memories'")
if tables:
    print(f'\nTable exists: {tables[0]["table_name"]}')
else:
    print('\nTable does not exist')
