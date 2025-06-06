#!/usr/bin/env python3
from agents.dreamfilter import DreamfilterEngine

# Check recent dreams structure
engine = DreamfilterEngine()
dreams = engine.get_recent_dreams('867410ee-6944-4b11-b958-0db79174f7e0', limit=2)

print(f'Recent dreams ({len(dreams)}):')
for i, d in enumerate(dreams):
    print(f'Dream {i+1} keys: {list(d.keys())}')
    if d:
        for key, value in d.items():
            if isinstance(value, str) and len(value) > 100:
                print(f'  {key}: {value[:80]}...')
            else:
                print(f'  {key}: {value}')
    print()
