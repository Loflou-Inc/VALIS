"""
Simple Update Memory Utility

This script is a simplified version that adds memories without depending on external libraries.
"""

import json
import os
import sys
import time
import hashlib

def main():
    """Main function to update memory"""
    if len(sys.argv) < 2:
        print("Error: No memory text provided.")
        print("Usage: python simple_update_memory.py \"Memory text to store\"")
        return
    
    # Get memory text from command line
    memory_text = " ".join(sys.argv[1:])
    
    # Skip if memory text is too short or just the MEMORY prefix
    if len(memory_text) < 10 or memory_text == "MEMORY:":
        print("Memory text too short, skipping.")
        return
    
    # Strip "MEMORY:" prefix if present
    if memory_text.startswith("MEMORY: "):
        memory_text = memory_text[8:]
    
    # Add the memory
    add_simple_memory(memory_text)

def add_simple_memory(text, important=False):
    """Add a simple memory without embeddings or complex processing"""
    memory_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_store", "memories.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)
    
    # Load existing memories
    try:
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
        else:
            memories = []
    except Exception as e:
        print(f"Error loading memory file: {e}")
        memories = []
    
    # Create content hash for deduplication
    content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    
    # Check for duplicates
    for memory in memories:
        if memory.get("hash") == content_hash or memory.get("text") == text:
            print("Duplicate memory, skipping.")
            return
    
    # Create timestamp and date
    timestamp = time.time()
    date_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a basic memory entry
    new_memory = {
        "timestamp": timestamp,
        "date": date_str,
        "text": text,
        "hash": content_hash,
        "tags": ["auto-tag"],
        "important": important
    }
    
    # Add to memories and save
    memories.append(new_memory)
    
    try:
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
        print(f"Added memory: {text}")
    except Exception as e:
        print(f"Error saving memory file: {e}")

if __name__ == "__main__":
    main()
