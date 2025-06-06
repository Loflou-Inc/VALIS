import sys
sys.path.append('valis2')
from memory.db import db

# Check reflection tables
tables = db.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%reflection%'")
print('Reflection tables:')
for table in tables:
    print(f'  - {table["table_name"]}')

# Check columns in reflection table  
if tables:
    table_name = tables[0]['table_name']
    columns = db.query(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    print(f'\n{table_name} columns:')
    for col in columns:
        print(f'  - {col["column_name"]}')
