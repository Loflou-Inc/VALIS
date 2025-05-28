"""
Claude Integration Module

This module provides the interface between Claude and the memory system.
It handles retrieving relevant memories and generating memory-enhanced prompts.
"""

from memory_manager import query_memories, add_memory, deep_search
import os
import time
from typing import Dict, Any, List, Optional

try:
    from config import PERSONA_NAME, PERSONA_DESCRIPTION, MEMORY_SEARCH_TOP_K
except ImportError:
    PERSONA_NAME = "Claude"
    PERSONA_DESCRIPTION = "An AI assistant with memory capabilities"
    MEMORY_SEARCH_TOP_K = 5

def get_memory_prompt(user_input: str, deep_context: bool = False) -> str:
    """
    Generate a memory-enhanced prompt for Claude
    
    Args:
        user_input: The user's message
        deep_context: Whether to use deep search (including archives)
        
    Returns:
        A formatted memory context for Claude
    """
    if deep_context:
        relevant_memories = deep_search(user_input, include_archives=True)
    else:
        relevant_memories = query_memories(user_input, top_k=MEMORY_SEARCH_TOP_K)
    
    if not relevant_memories:
        return "No specific memories to recall for this query."
    
    memory_text = "\n- ".join(relevant_memories)
    context = f"""
Relevant memories from previous conversations:
- {memory_text}

Remember that this information is from previous interactions, but don't explicitly
reference that you're using "memories" or that you've been "reminded" of something.
Just incorporate the information naturally into your response if relevant.
"""
    return context

def extract_key_info(user_input: str, claude_response: str) -> Optional[str]:
    """
    Simple extraction of key information from conversation
    Returns a memory-worthy string or None if nothing important
    
    This is a simplified version. In a real system, you might use more
    sophisticated NLP techniques or LLM-based extraction.
    """
    # Check for key phrases that might indicate important information
    key_phrases = [
        "my name is", "i am", "i'm", "i want", "i need", 
        "i prefer", "i like", "i don't like", "i dislike",
        "i'm working on", "my project", "the project", 
        "important", "remember", "don't forget",
        "created", "built", "developed", "implemented",
        "design", "architecture", "structure", "framework",
        "api", "endpoint", "interface", "database",
        "username", "password", "credential", "key",
        "problem", "issue", "error", "bug", "fix",
        "deadline", "schedule", "timeline", "milestone"
    ]
    
    # Look for key phrases in the user input
    for phrase in key_phrases:
        if phrase in user_input.lower():
            return user_input
    
    # If nothing important was detected
    return None

def process_conversation(user_input: str, claude_response: str) -> Optional[str]:
    """
    Process a conversation turn to extract and store important information
    
    Args:
        user_input: The user's message
        claude_response: Claude's response
        
    Returns:
        The memory text that was added, or None if no memory was added
    """
    # Extract key information from the conversation
    memory_text = extract_key_info(user_input, claude_response)
    
    # If important information was detected, store it
    if memory_text:
        add_memory(memory_text)
        return memory_text
    
    return None

def auto_remember(memory_text: str) -> None:
    """
    Wrapper function for conveniently adding memories from Claude
    
    Args:
        memory_text: The memory to add
    """
    add_memory(memory_text)

def auto_remember_important(memory_text: str) -> None:
    """
    Wrapper function for conveniently adding important memories from Claude
    
    Args:
        memory_text: The important memory to add
    """
    add_memory(memory_text, important=True)

# Quick demo function
def handle_user_message(user_input: str) -> str:
    """
    Example function to handle a user message, integrating memories
    This is for demonstration purposes only.
    
    Args:
        user_input: The user's message
        
    Returns:
        A simulated Claude response
    """
    # Get memories for context
    memory_prompt = get_memory_prompt(user_input)
    
    # This would be shown to Claude before generating a response
    print("===== MEMORY CONTEXT (CLAUDE EYES ONLY) =====")
    print(memory_prompt)
    print("============================================")
    
    # In a real implementation, Claude would now generate a response
    # using the memory context
    claude_response = "This is a simulated Claude response."
    
    # After Claude generates a response, process the conversation
    # to extract and store new memories
    new_memory = process_conversation(user_input, claude_response)
    
    if new_memory:
        print(f"Added new memory: {new_memory}")
    
    return claude_response

if __name__ == "__main__":
    # Simple demo
    test_input = "What was that project we were working on last week?"
    response = handle_user_message(test_input)
    print(f"Response: {response}")
