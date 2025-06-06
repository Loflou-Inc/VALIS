import sys
sys.path.append('valis2')
from memory.db import db

# Check unconscious_log schema
columns = db.query("SELECT column_name FROM information_schema.columns WHERE table_name = 'unconscious_log' ORDER BY ordinal_position")
print('unconscious_log columns:')
for col in columns:
    print(f'  - {col["column_name"]}')
