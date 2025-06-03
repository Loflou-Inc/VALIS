#!/usr/bin/env python3
"""Sprint 8B: Memory Data Seeding & Testing"""

import json
import sys
from pathlib import Path
import requests

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter

def seed_memory_data():
    """Seed memory with test data"""
    print("SEEDING MEMORY DATA...")
    
    memory_router = MemoryRouter()
    
    # Add canonical memories
    canon_entries = [
        "Successfully mediated conflict between engineering and marketing teams at TechCorp by identifying misaligned quarterly goals #canon",
        "Developed Systems Thinking Framework for HR challenges at GlobalManufacturing #canon", 
        "Engineering conflicts often stem from unclear technical requirements - now part of diagnostic checklist #canon"
    ]
    
    for entry in canon_entries:
        memory_router.canonize_response(
            persona_id="jane",
            response_text=entry,
            source_prompt="Memory seeding"
        )
    
    # Add client facts
    memory_router.add_client_fact("jane", "test_client", "role", "engineering_manager")
    memory_router.add_client_fact("jane", "test_client", "team_size", "8_engineers")
    memory_router.add_client_fact("jane", "test_client", "main_challenge", "team_communication")
    
    # Add working memory
    working_entries = [
        "Client shows signs of imposter syndrome - needs confidence building",
        "Team dynamics suggest need for structured 1-on-1 meetings",
        "Performance issues may be communication-related rather than technical"
    ]
    
    for entry in working_entries:
        memory_router.add_working_memory("jane", entry, "observation")
    
    print("Memory seeding complete!")

def test_memory_via_api():
    """Test memory via backend API"""
    print("\nTESTING MEMORY VIA API...")
    
    # Test memory endpoint
    response = requests.get("http://127.0.0.1:3001/api/memory/jane?session=test_session")
    if response.status_code == 200:
        memory = response.json()
        print(f"Core biography entries: {len(memory.get('core_biography', {}))}")
        print(f"Canon entries: {len(memory.get('canonized_identity', []))}")
        print(f"Client facts: {len(memory.get('client_profile', {}).get('facts', {}))}")
        print(f"Working memory: {len(memory.get('working_memory', []))}")
    else:
        print(f"Memory API failed: {response.status_code}")
    
    # Test chat with memory tags
    print("\nTesting chat with #canon tag...")
    chat_response = requests.post("http://127.0.0.1:3001/api/chat", json={
        "session_id": "test_session_canon",
        "persona_id": "jane",
        "message": "I successfully helped resolve the team's communication issues using structured meetings #canon"
    })
    
    if chat_response.status_code == 200:
        result = chat_response.json()
        print(f"Chat successful: {result.get('success')}")
        print(f"Provider: {result.get('provider')}")
        print(f"Tags processed: {result.get('memory_info', {}).get('tags_processed', [])}")
    else:
        print(f"Chat API failed: {chat_response.status_code}")

def main():
    print("SPRINT 8B: MEMORY SEEDING & TESTING")
    print("=" * 40)
    
    try:
        seed_memory_data()
        test_memory_via_api()
        
        print("\n" + "=" * 40)
        print("SEEDING COMPLETE - Frontend should now show:")
        print("- Jane's core biography (role, experience, approach)")
        print("- Canon memories from past successful interventions")
        print("- Working memory with current observations")
        print("- Client profile with test facts")
        print("\nRefresh frontend at http://127.0.0.1:3001")
        
    except Exception as e:
        print(f"FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
