#!/usr/bin/env python3
"""
Seed default personality profiles for VALIS personas
Sprint 12: Personality Expression Engine
"""
import sys
from pathlib import Path
import json
import uuid

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db

# Default personality profiles for VALIS personas
PERSONA_PERSONALITY_PROFILES = {
    "Kai the Coach": {
        "base_traits": {
            "extraversion": 0.8,
            "agreeableness": 0.7,
            "conscientiousness": 0.6,
            "emotional_stability": 0.7,
            "openness": 0.6
        },
        "description": "Energetic, confident, and supportive coach personality"
    },
    "Luna the Therapist": {
        "base_traits": {
            "extraversion": 0.4,
            "agreeableness": 0.8,
            "conscientiousness": 0.7,
            "emotional_stability": 0.5,
            "openness": 0.9
        },
        "description": "Thoughtful, empathetic, and creative assistant"
    },
    "Jane Thompson": {
        "base_traits": {
            "extraversion": 0.6,
            "agreeableness": 0.6,
            "conscientiousness": 0.9,
            "emotional_stability": 0.8,
            "openness": 0.7
        },
        "description": "Professional, organized, and systematic HR partner"
    }
}

def get_persona_uuid(persona_name: str) -> str:
    """Get the UUID for a persona by name"""
    try:
        result = db.query("SELECT id FROM persona_profiles WHERE name ILIKE %s", (persona_name,))
        if result:
            return str(result[0]['id'])
        else:
            print(f"[-] Persona '{persona_name}' not found in database")
            return None
    except Exception as e:
        print(f"[-] Error looking up persona {persona_name}: {e}")
        return None

def seed_personality_profiles():
    """Create personality profiles for existing personas"""
    print("Seeding personality profiles for VALIS personas...")
    
    created_count = 0
    
    for persona_name, profile_data in PERSONA_PERSONALITY_PROFILES.items():
        try:
            # Get persona UUID
            persona_uuid = get_persona_uuid(persona_name)
            if not persona_uuid:
                continue
            
            print(f"Creating personality profile for {persona_name} ({persona_uuid})")
            
            # Insert personality profile
            db.execute("""
                INSERT INTO agent_personality_profiles 
                (persona_id, base_traits, learned_modifiers, interaction_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (persona_id) DO UPDATE SET
                    base_traits = EXCLUDED.base_traits,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                persona_uuid,
                json.dumps(profile_data['base_traits']),
                json.dumps({}),  # Empty learned modifiers initially
                0
            ))
            
            print(f"[+] Created personality profile for {persona_name}")
            created_count += 1
            
        except Exception as e:
            print(f"[-] Failed to create personality profile for {persona_name}: {e}")
    
    print(f"\n[+] Successfully created {created_count} personality profiles")
    return created_count > 0

def verify_personality_data():
    """Verify the personality data was created correctly"""
    print("\nVerifying personality profiles...")
    
    try:
        profiles = db.query("""
            SELECT p.name, pp.base_traits, pp.learned_modifiers, pp.created_at
            FROM agent_personality_profiles pp
            JOIN persona_profiles p ON pp.persona_id = p.id
            ORDER BY p.name
        """)
        
        if profiles:
            print(f"[+] Found {len(profiles)} personality profiles:")
            for profile in profiles:
                traits = profile['base_traits']
                print(f"    - {profile['name']}: extraversion={traits.get('extraversion', 0):.1f}, "
                      f"agreeableness={traits.get('agreeableness', 0):.1f}")
        else:
            print("[-] No personality profiles found")
            
        # Check tone templates
        tones = db.query("SELECT tone_id, tone_name FROM personality_tone_templates ORDER BY tone_id")
        print(f"[+] Available personality tones: {', '.join([t['tone_id'] for t in tones])}")
        
        return len(profiles) > 0
        
    except Exception as e:
        print(f"[-] Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("=== VALIS PERSONALITY ENGINE SEED DATA ===")
    
    success = seed_personality_profiles()
    if success:
        verify_personality_data()
        print("\n[+] Personality Engine seed data complete!")
    else:
        print("\n[-] Personality Engine seeding failed")
        sys.exit(1)
