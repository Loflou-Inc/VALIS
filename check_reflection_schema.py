import sys
sys.path.append('valis2')
from memory.db import db

columns = db.query("SELECT column_name, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'agent_reflection_log' ORDER BY ordinal_position")
print('agent_reflection_log schema:')
for col in columns:
    nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ''
    print(f'  {col["column_name"]}: {nullable}{default}')
