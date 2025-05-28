"""
Claude Memory Desktop Commander Integration

This module provides a command-line interface for using the memory system
with Claude's Desktop Commander capabilities.
"""

import sys
import os
import time
from memory_manager import add_memory, query_memories, deep_search, mark_important, memory_health_report

def print_usage():
    """Print usage instructions"""
    print("Claude Memory System - Desktop Commander Interface")
    print("Usage:")
    print("  remember <text>       - Add a new memory")
    print("  important <text>      - Add an important memory (won't be archived)")
    print("  mark <text>           - Mark an existing memory as important")
    print("  recall <query>        - Search for relevant memories")
    print("  deep <query>          - Perform a deep search (including archives)")
    print("  context <query>       - Get memory context for Claude prompt")
    print("  list                  - List all memories")
    print("  health                - Show memory system health")
    print("  help                  - Show this help message")

def format_memory_for_claude(memories):
    """Format memories in a way that's easy for Claude to read"""
    if not memories:
        return "No relevant memories found."
    
    return "\n\n".join([f"* {m}" for m in memories])

def main():
    """Main entry point for command-line interface"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "remember":
        if len(sys.argv) < 3:
            print("Error: Missing memory text")
            print_usage()
            return
        
        memory_text = " ".join(sys.argv[2:])
        add_memory(memory_text)
        print(f"Added memory: {memory_text}")
        
    elif command == "important":
        if len(sys.argv) < 3:
            print("Error: Missing memory text")
            print_usage()
            return
        
        memory_text = " ".join(sys.argv[2:])
        add_memory(memory_text, important=True)
        print(f"Added important memory: {memory_text}")
        
    elif command == "mark":
        if len(sys.argv) < 3:
            print("Error: Missing memory text")
            print_usage()
            return
        
        memory_text = " ".join(sys.argv[2:])
        success = mark_important(memory_text)
        if success:
            print(f"Marked memory containing '{memory_text}' as important")
        else:
            print(f"No memory found containing '{memory_text}'")
            
    elif command == "recall":
        if len(sys.argv) < 3:
            print("Error: Missing query text")
            print_usage()
            return
        
        query = " ".join(sys.argv[2:])
        memories = query_memories(query)
        print("Memory recall results:")
        print(format_memory_for_claude(memories))
        
    elif command == "deep":
        if len(sys.argv) < 3:
            print("Error: Missing query text")
            print_usage()
            return
        
        query = " ".join(sys.argv[2:])
        memories = deep_search(query)
        print("Deep memory search results:")
        print(format_memory_for_claude(memories))
        
    elif command == "context":
        if len(sys.argv) < 3:
            print("Error: Missing query text")
            print_usage()
            return
        
        query = " ".join(sys.argv[2:])
        memories = query_memories(query)
        
        # Format for Claude prompt
        if memories:
            print("=== MEMORY CONTEXT (CLAUDE EYES ONLY) ===")
            print("Claude, consider these relevant memories from previous conversations:")
            print(format_memory_for_claude(memories))
            print("Use this information naturally in your response without explicitly mentioning that you're using memories.")
            print("===========================================")
        else:
            print("No relevant memories found for this query.")
            
    elif command == "list":
        # Import load_memory function only when needed
        from memory_manager import load_memory
        memories = load_memory()
        
        if not memories:
            print("No memories found in the system.")
            return
            
        print(f"All memories ({len(memories)}):")
        for m in memories:
            imp = "[IMPORTANT] " if m.get("important", False) else ""
            date = m.get("date", "Unknown date")
            text = m.get("text", "")
            print(f"* {imp}[{date}] {text}")
            
    elif command == "health":
        report = memory_health_report()
        print(report)
        
    elif command == "help":
        print_usage()
        
    else:
        print(f"Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main()
