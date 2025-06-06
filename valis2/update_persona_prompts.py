#!/usr/bin/env python3
"""
Update persona prompts to include tool capabilities
"""
import sys
from pathlib import Path

# Add valis2 to path
valis2_dir = Path(__file__).parent
sys.path.append(str(valis2_dir))

from memory.db import db

def update_persona_prompts():
    """Add tool capabilities to persona system prompts"""
    
    # Get current personas
    personas = db.query("SELECT id, name, system_prompt FROM persona_profiles ORDER BY name")
    
    print(f"Found {len(personas)} personas to update:")
    
    tool_capabilities_text = """

TOOL CAPABILITIES:
You have access to local tools that can help you provide better assistance:
- Memory Search: Query your knowledge base for specific topics
- File Reading: Read and analyze local files  
- File Search: Find files by name or content
- Directory Listing: Browse local file structures

Use these tools naturally when they would be helpful for the user's request."""
    
    for persona in personas:
        current_prompt = persona['system_prompt'] or ""
        
        # Check if tools are already mentioned
        if "TOOL CAPABILITIES" in current_prompt or "memory search" in current_prompt.lower():
            print(f"  {persona['name']}: Already has tool capabilities")
            continue
        
        # Add tool capabilities to prompt
        updated_prompt = current_prompt + tool_capabilities_text
        
        # Update in database
        db.execute("""
            UPDATE persona_profiles 
            SET system_prompt = %s 
            WHERE id = %s
        """, (updated_prompt, persona['id']))
        
        print(f"  {persona['name']}: Updated with tool capabilities")
    
    print("Persona prompt updates complete!")

if __name__ == "__main__":
    update_persona_prompts()
