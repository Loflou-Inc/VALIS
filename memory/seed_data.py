"""
VALIS 2.0 Database Seeder
Populate sample personas, memories, and client data
"""
import os
import sys
from pathlib import Path

# Add valis2 directory to path
valis2_dir = Path(__file__).parent.parent
sys.path.append(str(valis2_dir))

from memory.db import db
import json
import uuid
from datetime import datetime, timedelta

def seed_personas():
    """Create sample personas with different context modes"""
    personas = [
        {
            'name': 'Kai the Coach',
            'role': 'Personal Development Coach',
            'bio': 'Experienced life coach specializing in goal achievement and motivation',
            'system_prompt': 'You are Kai, an energetic personal coach focused on helping people achieve their goals.',
            'default_context_mode': 'balanced',
            'traits': json.dumps({
                'energy_level': 'high',
                'communication_style': 'encouraging',
                'specialties': ['goal_setting', 'motivation', 'accountability']
            })
        },
        {
            'name': 'Luna the Therapist',
            'role': 'Mental Health Counselor',
            'bio': 'Licensed therapist with expertise in anxiety, depression, and mindfulness practices',
            'system_prompt': 'You are Luna, a calm and empathetic therapist focused on mental wellness.',
            'default_context_mode': 'full',
            'traits': json.dumps({
                'energy_level': 'calm',
                'communication_style': 'empathetic',
                'specialties': ['anxiety', 'depression', 'mindfulness']
            })
        },
        {
            'name': 'Jane Thompson',
            'role': 'HR Business Partner', 
            'bio': 'Experienced HR professional with 15 years in talent development',
            'system_prompt': 'You are Jane, a professional HR expert focused on workplace solutions.',
            'default_context_mode': 'tight',
            'traits': json.dumps({
                'energy_level': 'professional',
                'communication_style': 'direct',
                'specialties': ['talent_development', 'performance_management', 'workplace_culture']
            })
        }
    ]
    
    persona_ids = {}
    for persona in personas:
        try:
            persona_id = db.insert('persona_profiles', persona)
            persona_ids[persona['name']] = persona_id
            print(f"OK Created persona: {persona['name']} (ID: {persona_id}) [Mode: {persona['default_context_mode']}]")
        except Exception as e:
            print(f"ERROR Failed to create {persona['name']}: {e}")
    
    return persona_ids

def seed_canon_memories(persona_ids):
    """Create sample canon memories"""
    kai_id = persona_ids.get('Kai the Coach')
    luna_id = persona_ids.get('Luna the Therapist') 
    jane_id = persona_ids.get('Jane Thompson')
    
    if not kai_id or not luna_id or not jane_id:
        print("ERROR: Missing persona IDs for canon memories")
        return
    
    memories = [
        # Kai's coaching knowledge
        {
            'persona_id': kai_id,
            'content': 'SMART goals framework: Specific, Measurable, Achievable, Relevant, Time-bound',
            'tags': ['goal_setting', 'framework'],
            'category': 'methodology',
            'relevance_score': 0.9
        },
        {
            'persona_id': kai_id, 
            'content': 'The 1% better principle: Small daily improvements compound over time',
            'tags': ['improvement', 'habits'],
            'category': 'philosophy',
            'relevance_score': 0.8
        },
        # Luna's therapy knowledge
        {
            'persona_id': luna_id,
            'content': 'Box breathing technique: Inhale 4, hold 4, exhale 4, hold 4 for anxiety relief',
            'tags': ['anxiety', 'breathing', 'technique'],
            'category': 'coping_skill',
            'relevance_score': 0.9
        },
        # Jane's HR knowledge
        {
            'persona_id': jane_id,
            'content': 'Performance reviews should focus on specific behaviors and outcomes, not personality',
            'tags': ['performance', 'feedback'],
            'category': 'best_practice',
            'relevance_score': 0.8
        }
    ]
    
    for memory in memories:
        try:
            memory_id = db.insert('canon_memories', memory)
            print(f"OK Created canon memory (ID: {memory_id})")
        except Exception as e:
            print(f"ERROR Failed to create canon memory: {e}")


def seed_test_client():
    """Create test client profile"""
    client_data = {
        'name': 'Alex Chen',
        'email': 'alex@example.com',
        'traits': json.dumps({
            'goals': ['improve_productivity', 'reduce_stress'],
            'personality': 'analytical',
            'communication_preference': 'direct'
        })
    }
    
    try:
        client_id = db.insert('client_profiles', client_data)
        print(f"OK Created test client: {client_data['name']} (ID: {client_id})")
        return client_id
    except Exception as e:
        print(f"ERROR Failed to create test client: {e}")
        return None

def seed_working_memory(persona_ids, client_id):
    """Create sample working memory entries"""
    kai_id = persona_ids.get('Kai the Coach')
    
    if not kai_id or not client_id:
        print("ERROR: Missing persona or client ID for working memory")
        return
    
    working_entries = [
        {
            'persona_id': kai_id,
            'client_id': client_id,
            'content': 'Alex mentioned feeling overwhelmed with work deadlines this week',
            'importance': 7,
            'expires_at': datetime.now() + timedelta(days=7)
        },
        {
            'persona_id': kai_id,
            'client_id': client_id, 
            'content': 'Goal set: Complete project proposal by Friday',
            'importance': 8,
            'expires_at': datetime.now() + timedelta(days=5)
        }
    ]
    
    for entry in working_entries:
        try:
            entry_id = db.insert('working_memory', entry)
            print(f"OK Created working memory entry (ID: {entry_id})")
        except Exception as e:
            print(f"ERROR Failed to create working memory: {e}")

def run_seeder():
    """Run all seeder functions"""
    print("SEED Starting VALIS 2.0 database seeding...")
    persona_ids = seed_personas()
    seed_canon_memories(persona_ids)
    client_id = seed_test_client()
    seed_working_memory(persona_ids, client_id)
    print("OK Database seeding complete!")

if __name__ == "__main__":
    run_seeder()
