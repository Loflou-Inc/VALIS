import sys
sys.path.append('C:\\VALIS\\valis2')
from memory.db import db

# Query for Jane persona in main database
jane_personas = db.query(
    "SELECT id, name, role, bio, traits FROM persona_profiles WHERE name = 'Jane'"
)

print(f"Found {len(jane_personas)} Jane personas in main database:")
for jane in jane_personas:
    print(f"\nJane Persona:")
    print(f"  ID: {jane['id']}")
    print(f"  Name: {jane['name']}")
    print(f"  Role: {jane['role']}")
    print(f"  Bio: {jane['bio']}")
    if jane['traits']:
        import json
        traits = json.loads(jane['traits']) if isinstance(jane['traits'], str) else jane['traits']
        print(f"  Archetypes: {traits.get('archetypes', [])}")
        print(f"  Domains: {traits.get('domains', [])}")
        print(f"  Vault Source: {traits.get('vault_source', False)}")
