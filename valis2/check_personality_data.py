#!/usr/bin/env python3
from memory.db import db

# Check personality profiles
profiles = db.query('SELECT * FROM agent_personality_profiles')
print(f'Found {len(profiles)} personality profiles:')
for p in profiles:
    print(f'  {p["persona_id"]} - {p["base_traits"]}')

# Check tone templates
tones = db.query('SELECT tone_id, tone_name FROM personality_tone_templates')
print(f'\nFound {len(tones)} tone templates:')
for t in tones:
    print(f'  {t["tone_id"]} - {t["tone_name"]}')
