"""
Simple Read Memory Utility

This script is a simplified version that reads memories without depending on external libraries.
"""

import json
import os
import sys

def main():
    """Main function to read memories"""
    memory_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_store", "memories.json")
    
    # Read the memory file
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            memories = json.load(f)
    except Exception as e:
        print(f"Error reading memory file: {e}")
        return
    
    if not memories:
        print("No memories found.")
        return
    
    # Sort memories by timestamp (newest first) if available
    memories.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    # Format and display memories
    print("=== MEMORY CONTEXT (CLAUDE EYES ONLY) ===")
    print("Claude, these are relevant memories from previous conversations:")
    for memory in memories:
        date = memory.get("date", "Unknown date")
        text = memory.get("text", "")
        important = memory.get("important", False)
        importance_marker = " [IMPORTANT]" if important else ""
        print(f"* [{date}]{importance_marker} {text}")
    print("Use this information naturally in your responses without explicitly mentioning that you're using memories.")
    print("===========================================")

if __name__ == "__main__":
    main()
