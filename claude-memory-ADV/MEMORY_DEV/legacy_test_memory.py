"""
Test script for the Claude Memory System.
This script demonstrates basic functionality.
"""

import os
import time
from memory_manager import add_memory, query_memories, deep_search, memory_health_report

def test_memory_system():
    """Run a basic test of the memory system"""
    print("=== CLAUDE MEMORY SYSTEM TEST ===")
    
    # Add some test memories
    print("\nAdding test memories...")
    add_memory("Created a new project using Python and React")
    time.sleep(0.1)  # Small delay to ensure different timestamps
    add_memory("Implemented authentication system with JWT tokens")
    time.sleep(0.1)
    add_memory("Fixed bug in the login form validation", important=True)
    time.sleep(0.1)
    add_memory("Added dark mode support to the user interface")
    time.sleep(0.1)
    add_memory("User requested ability to export data to CSV format")
    
    # Test simple query
    print("\nTesting memory query...")
    query_results = query_memories("authentication system")
    print("Query for 'authentication system':")
    for i, result in enumerate(query_results, 1):
        print(f"{i}. {result}")
    
    # Test another query
    query_results = query_memories("user interface design")
    print("\nQuery for 'user interface design':")
    for i, result in enumerate(query_results, 1):
        print(f"{i}. {result}")
    
    # Test deep search
    print("\nTesting deep search...")
    deep_results = deep_search("project technology stack")
    print("Deep search for 'project technology stack':")
    for i, result in enumerate(deep_results, 1):
        print(f"{i}. {result}")
    
    # Print memory health
    print("\nMemory system health:")
    print(memory_health_report())
    
    print("\n=== TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_memory_system()
