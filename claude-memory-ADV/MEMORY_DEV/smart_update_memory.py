"""
Session-aware memory management utility.
"""

import json
import os
import sys
import time

def add_memory(text, important=False):
    """Add a new memory with intelligent deduplication"""
    memory_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_store", "memories.json")
    
    # Read existing memories
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            memories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memories = []
    
    # Check if this memory already exists in recent entries (last 3)
    recent_memories = memories[:3] if memories else []
    for memory in recent_memories:
        if memory.get("text") == text:
            print(f"Memory already exists: {text}")
            return False
    
    # Create new memory
    timestamp = time.time()
    date_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create simple hash for reference
    import hashlib
    hash_text = hashlib.md5(text.encode()).hexdigest()[:12]
    
    new_memory = {
        "timestamp": timestamp,
        "date": date_str,
        "text": text,
        "hash": hash_text,
        "tags": ["auto-tag"],
        "important": important
    }
    
    # Add to memory list
    memories.insert(0, new_memory)
    
    # Save updated memories
    try:
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2)
        print(f"Memory added: {text}")
        return True
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False

def update_init_state():
    """Create or update initialization state file"""
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_state.txt")
    with open(state_file, 'w', encoding='utf-8') as f:
        f.write(f"initialized=true\ntime={time.time()}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_update_memory.py \"Memory text\"")
        sys.exit(1)
    
    memory_text = sys.argv[1]
    
    if memory_text.startswith("INIT_ONLY"):
        # Just update the init state without adding a memory
        update_init_state()
        print("Initialization state updated.")
    else:
        # Normal memory addition
        important = "--important" in sys.argv
        success = add_memory(memory_text, important=important)
        if success:
            update_init_state()
