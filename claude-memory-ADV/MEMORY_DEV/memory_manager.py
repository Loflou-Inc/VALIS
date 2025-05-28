"""
Claude Memory Manager - Optimized Version
-----------------------------------
A hybrid memory system with dual architecture:
1. Flat-file ledger (JSON) - Human-readable canonical source of truth
2. Vector-based similarity search for semantic recall (ChromaDB when available)

This system helps Claude maintain context across conversations.
"""

import json
import os
import sys
import time
import math
import re
import hashlib
from typing import List, Dict, Any, Optional, Union, Set, Tuple
import traceback

# Import configuration
try:
    from config import (
        MAX_MEMORY_WORDS, EMBEDDING_MODEL, MAX_FILE_SIZE_KB, 
        ARCHIVE_THRESHOLD, USE_TAGS, USE_CHROMADB, CHROMA_PERSIST_DIR,
        MEMORY_SEARCH_TOP_K, DEEP_SEARCH_TOP_K
    )
except ImportError:
    # Default values if config import fails
    MAX_MEMORY_WORDS = 25
    EMBEDDING_MODEL = "sentence-transformer"
    MAX_FILE_SIZE_KB = 200
    ARCHIVE_THRESHOLD = 100
    USE_TAGS = True
    USE_CHROMADB = True
    CHROMA_PERSIST_DIR = "memory_store/.chroma"
    MEMORY_SEARCH_TOP_K = 5
    DEEP_SEARCH_TOP_K = 10

# Path to the memory file and directory
MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_store")
MEMORY_FILE = os.path.join(MEMORY_DIR, "memories.json")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")

# Set of action verbs for tagging
ACTION_VERBS = {
    "add", "update", "create", "delete", "remove", "move", "copy", "archive", 
    "implement", "build", "enhance", "improve", "modify", "change", "refactor", 
    "clean", "organize", "setup", "test", "verify", "fixed", "patched", "renamed",
    "analyzed", "discussed", "explained", "cleaned", "reorganized", "enabled",
    "disabled", "upgraded", "downgraded", "configured", "developed", "completed"
}

# Initialize embedding model - try sentence-transformers first
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    USE_SBERT = True
    print("Using sentence-transformers for embeddings.")
    
    def get_embedding(text: str) -> List[float]:
        """Get embedding using sentence-transformers"""
        return model.encode(text).tolist()
except ImportError:
    USE_SBERT = False
    print("WARNING: sentence-transformers not available.")
    print("Using simple keyword matching fallback.")
    
    def get_embedding(text: str) -> List[float]:
        """Simple fallback that creates a pseudo-embedding based on word hashes"""
        # This is not a real embedding, just a placeholder
        words = set(text.lower().split())
        # Create a simple vector from word hashes
        return [hash(word) % 10000 / 10000 for word in words] + [0] * (384 - len(words))

# Initialize ChromaDB if enabled
CHROMA_ENABLED = False
if USE_CHROMADB:
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Ensure persistence directory exists
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), CHROMA_PERSIST_DIR), exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        memory_collection = chroma_client.get_or_create_collection("claude_memories")
        CHROMA_ENABLED = True
        print("ChromaDB initialized successfully.")
    except Exception as e:
        print(f"Could not initialize ChromaDB: {e}")
        print("Falling back to flat-file only mode.")

# Comprehensive stopwords list
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
    "at", "by", "for", "with", "about", "against", "between", "into", "through", 
    "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", 
    "once", "here", "there", "when", "where", "why", "how", "all", "any", 
    "both", "each", "few", "more", "most", "other", "some", "such", "no", 
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", 
    "t", "can", "will", "just", "don", "don't", "should", "now", "memory",
    "system", "claude", "using", "used"
}

def extract_tags(text: str) -> List[str]:
    """
    Extract semantic tags from text:
    1. Check for action verbs
    2. Extract filesystem and coding terms
    3. Extract other key operational terms
    """
    if not USE_TAGS:
        return []
        
    tags = []
    words = text.lower().split()
    
    # Check for action verbs
    for word in words:
        # Remove trailing punctuation
        clean_word = word.rstrip('.,;:!?')
        if clean_word in ACTION_VERBS:
            tags.append(clean_word)
    
    # Check for filesystem operations
    filesystem_patterns = ["file", "folder", "directory", "path", "archive", "zip"]
    for pattern in filesystem_patterns:
        if pattern in text.lower():
            tags.append(pattern)
    
    # Check for additional operational keywords
    operational_keywords = {
        "github": ["github", "git", "repository"],
        "git": ["commit", "push", "pull", "branch", "merge"],
        "testing": ["test", "unit test", "integration test", "qa"],
        "documentation": ["document", "documentation", "readme", "manual"],
        "coding": ["code", "function", "class", "method", "api"],
        "database": ["database", "sql", "query", "record", "table"],
        "web": ["web", "website", "html", "css", "javascript"],
        "analysis": ["analyze", "analysis", "examine", "review", "assess"],
        "project": ["project", "task", "milestone", "deadline", "schedule"]
    }
    
    for category, keywords in operational_keywords.items():
        for keyword in keywords:
            if keyword in text.lower():
                tags.append(category)
                break
    
    # De-duplicate and return
    return list(set(tags))

def compute_content_hash(text: str) -> str:
    """Compute a short hash of the content for deduplication"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

def standardize_memory_text(text: str, max_words: int = MAX_MEMORY_WORDS) -> str:
    """
    Standardize memory text for better embedding:
    1. Ensure it starts with an action verb if possible
    2. Cap at specified max words
    3. Remove unnecessary prefixes
    """
    # Remove "MEMORY: " prefix if present
    if text.startswith("MEMORY: "):
        text = text[8:]
    
    # Split into words and cap at max_words
    words = text.split()[:max_words]
    
    # Check if first word is an action verb, if not and another action verb exists, try to rearrange
    if words and words[0].lower().rstrip('.,;:!?') not in ACTION_VERBS:
        for i, word in enumerate(words[1:], 1):
            if word.lower().rstrip('.,;:!?') in ACTION_VERBS:
                # Move this verb to the front and rearrange
                verb_phrase = words[i:]
                context_phrase = words[:i]
                words = verb_phrase + context_phrase
                break
    
    return " ".join(words)

def preprocess_memory_text(text: str) -> str:
    """
    Preprocess memory text for embedding:
    1. Cap at MAX_MEMORY_WORDS words
    2. Remove stop words
    """
    # Limit to MAX_MEMORY_WORDS words
    words = text.split()[:MAX_MEMORY_WORDS]
    
    # Remove stop words
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    
    # Rejoin text
    return " ".join(filtered_words)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    # Use vectors of the same length by padding the shorter one
    max_len = max(len(v1), len(v2))
    v1_padded = v1 + [0] * (max_len - len(v1))
    v2_padded = v2 + [0] * (max_len - len(v2))
    
    dot_product = sum(a * b for a, b in zip(v1_padded, v2_padded))
    magnitude1 = math.sqrt(sum(a * a for a in v1_padded))
    magnitude2 = math.sqrt(sum(b * b for b in v2_padded))
    
    if magnitude1 * magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def load_memory() -> List[Dict[str, Any]]:
    """Load the memory file"""
    try:
        # Ensure the memory directory exists
        os.makedirs(MEMORY_DIR, exist_ok=True)
        
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception:
        print(f"Error loading memory file: {traceback.format_exc()}")
        return []

def save_memory(memories: List[Dict[str, Any]]) -> None:
    """Save the memory file"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
    except Exception:
        print(f"Error saving memory file: {traceback.format_exc()}")

def estimate_tokens(text: str) -> int:
    """Roughly estimate the number of tokens in a text"""
    # A simple approximation: 1 token ≈ 4 characters for English text
    return len(text) // 4

def add_memory(text: str, important: bool = False) -> None:
    """Add a new memory to the system
    
    Args:
        text: The memory text to store
        important: If True, memory will be marked as important and never automatically archived
    """
    if not text:
        return
    
    # Standardize text format (action verb first, max_words limit)
    standardized_text = standardize_memory_text(text)
    
    # Calculate content hash for deduplication
    content_hash = compute_content_hash(standardized_text)
    
    # Extract tags
    tags = extract_tags(standardized_text)
    
    # Load existing memory data
    memories = load_memory()
    
    # Check for duplicates using content hash
    for memory in memories:
        if memory.get("hash") == content_hash:
            print(f"Duplicate memory entry detected (hash: {content_hash}). Skipping.")
            return
    
    # Create a timestamp for unique ID
    timestamp = time.time()
    date_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Preprocess for embedding
    processed_text = preprocess_memory_text(standardized_text)
    embedding = get_embedding(processed_text)
    
    # Create a new memory entry
    new_memory = {
        "timestamp": timestamp,
        "date": date_str,
        "text": standardized_text,
        "hash": content_hash,
        "tags": tags,
        "embedding": embedding,
        "important": important  # Mark as important if specified
    }
    
    # Add the new memory to the flat-file
    memories.append(new_memory)
    
    # Save the updated memories to JSON
    save_memory(memories)
    print(f"Added new memory: '{standardized_text}'")
    
    # Also add to ChromaDB if available
    if CHROMA_ENABLED:
        try:
            # Generate a unique ID with millisecond precision
            unique_id = f"{int(timestamp * 1000)}"
            
            # Add to ChromaDB collection
            # Convert tags list to string to avoid ChromaDB metadata type error
            tags_str = ",".join(tags) if tags else ""
            memory_collection.add(
                documents=[standardized_text],
                embeddings=[embedding],
                metadatas=[{
                    "date": date_str, 
                    "timestamp": timestamp,
                    "tags": tags_str,
                    "hash": content_hash,
                    "important": str(important).lower()
                }],
                ids=[unique_id]
            )
            print(f"Added memory to ChromaDB with ID: {unique_id}")
        except Exception as e:
            print(f"Error adding to ChromaDB: {e}")
            # Continue even if ChromaDB fails - flat-file is source of truth
    
    # Check file size and archive if necessary
    if os.path.exists(MEMORY_FILE):
        file_size_kb = os.path.getsize(MEMORY_FILE) / 1024
        
        if file_size_kb > ARCHIVE_THRESHOLD and len(memories) > 10:
            archive_old_memories(memories)

def archive_old_memories(memories: List[Dict[str, Any]]) -> None:
    """Archive older non-important memories to keep the main file size manageable"""
    # Create archive directory if it doesn't exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Determine how many memories to archive (50% of non-important ones)
    non_important = [m for m in memories if not m.get("important", False)]
    important = [m for m in memories if m.get("important", False)]
    
    # Calculate how many to archive (50% of non-important, rounded down)
    archive_count = max(len(non_important) // 2, 5)  # At least 5, at most 50%
    
    # Don't archive if we don't have enough non-important memories
    if len(non_important) <= 10:
        return
    
    # Select oldest non-important memories to archive
    non_important.sort(key=lambda x: x.get("timestamp", 0))
    to_archive = non_important[:archive_count]
    
    # Create archive file with timestamp
    archive_timestamp = int(time.time())
    archive_file = os.path.join(ARCHIVE_DIR, f"memory_archive_{archive_timestamp}.json")
    
    # Add metadata to the archive
    archive_data = {
        "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(archive_timestamp)),
        "count": len(to_archive),
        "date_range": {
            "start": to_archive[0].get("date", "Unknown") if to_archive else "Unknown",
            "end": to_archive[-1].get("date", "Unknown") if to_archive else "Unknown"
        },
        "memories": to_archive
    }
    
    # Save the archive file
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
    print(f"Archived {len(to_archive)} memories to {archive_file}")
    
    # Update the main memory file to exclude the archived memories
    # Keep important memories and non-archived non-important ones
    remaining_non_important = non_important[archive_count:]
    updated_memories = important + remaining_non_important
    
    # Sort by timestamp
    updated_memories.sort(key=lambda x: x.get("timestamp", 0))
    
    # Save the updated memories
    save_memory(updated_memories)

def query_memories(query: str, top_k: int = MEMORY_SEARCH_TOP_K) -> List[str]:
    """
    Query the memory system for relevant memories
    Uses ChromaDB for vector search if available, falls back to flat-file if not
    
    Args:
        query: The query text to search for
        top_k: Number of results to return
        
    Returns:
        List of memory text strings in order of relevance
    """
    if not query:
        return []
    
    # Try to use ChromaDB for semantic search if available
    if CHROMA_ENABLED:
        try:
            # Get query embedding
            query_embedding = get_embedding(preprocess_memory_text(query))
            
            # Query ChromaDB
            results = memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            if results and results["documents"] and results["documents"][0]:
                memories = []
                
                for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
                    date = meta.get("date", "Unknown date")
                    tag_str = meta.get("tags", "")
                    tag_info = f" [Tags: {tag_str}]" if tag_str else ""
                    
                    memory = f"[{date}] {doc}{tag_info}"
                    memories.append(memory)
                
                return memories
                
            print("ChromaDB query returned no results, falling back to flat-file.")
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            print("Falling back to flat-file retrieval.")
    
    # Fallback to flat-file search
    memories = load_memory()
    
    if not memories:
        return []
    
    # Get query embedding
    query_embedding = get_embedding(preprocess_memory_text(query))
    
    # Calculate similarity scores for all memories
    scored_memories = []
    for memory in memories:
        # Get memory embedding
        memory_embedding = memory.get("embedding", [])
        
        # If no embedding stored (shouldn't happen), generate one
        if not memory_embedding:
            memory_text = memory.get("text", "")
            memory_embedding = get_embedding(preprocess_memory_text(memory_text))
            
        # Calculate similarity
        similarity = cosine_similarity(query_embedding, memory_embedding)
        scored_memories.append((memory, similarity))
    
    # Sort by relevance (highest similarity first)
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    
    # Format the top k results
    results = []
    for memory, _ in scored_memories[:top_k]:
        date = memory.get("date", "Unknown date")
        text = memory.get("text", "")
        
        # Format tags if present
        tags = memory.get("tags", [])
        tag_str = ", ".join(tags) if tags else ""
        tag_info = f" [Tags: {tag_str}]" if tag_str else ""
        
        results.append(f"[{date}] {text}{tag_info}")
    
    return results

def deep_search(query: str, include_archives: bool = True, top_k: int = DEEP_SEARCH_TOP_K) -> List[str]:
    """
    Deep search through both current memory and archives
    
    Args:
        query: The query text to search for
        include_archives: Whether to include archived memories
        top_k: Number of results to return per source
        
    Returns:
        List of memory text strings in order of relevance
    """
    # Get results from current memory
    current_results = query_memories(query, top_k)
    
    # If archives not requested, return just current results
    if not include_archives:
        return current_results
    
    # Check if archive directory exists
    if not os.path.exists(ARCHIVE_DIR):
        return current_results
    
    # Get query embedding
    query_embedding = get_embedding(preprocess_memory_text(query))
    
    # Collect results from all archive files
    archive_scored_memories = []
    
    for filename in os.listdir(ARCHIVE_DIR):
        if filename.startswith("memory_archive_") and filename.endswith(".json"):
            archive_path = os.path.join(ARCHIVE_DIR, filename)
            
            try:
                with open(archive_path, 'r', encoding='utf-8') as f:
                    archive_data = json.load(f)
                
                for memory in archive_data.get("memories", []):
                    # Get memory embedding
                    memory_embedding = memory.get("embedding", [])
                    
                    # If no embedding stored, generate one
                    if not memory_embedding:
                        memory_text = memory.get("text", "")
                        memory_embedding = get_embedding(preprocess_memory_text(memory_text))
                        
                    # Calculate similarity
                    similarity = cosine_similarity(query_embedding, memory_embedding)
                    archive_scored_memories.append((memory, similarity, filename))
            except Exception as e:
                print(f"Error processing archive {filename}: {e}")
    
    # Sort all archive results by similarity
    archive_scored_memories.sort(key=lambda x: x[1], reverse=True)
    
    # Format the top k archive results
    archive_results = []
    for memory, _, archive_file in archive_scored_memories[:top_k]:
        date = memory.get("date", "Unknown date")
        text = memory.get("text", "")
        
        # Format tags if present
        tags = memory.get("tags", [])
        if isinstance(tags, str) and tags:
            tags = tags.split(",")
        tag_str = ", ".join(tags) if tags else ""
        tag_info = f" [Tags: {tag_str}]" if tag_str else ""
        
        archive_results.append(f"[ARCHIVED] [{date}] {text}{tag_info}")
    
    # Combine current and archive results
    # - If we have a lot of results, interleave them
    # - Otherwise just append archive results
    if len(current_results) >= top_k // 2:
        # Interleave results
        combined = []
        for i in range(max(len(current_results), len(archive_results))):
            if i < len(current_results):
                combined.append(current_results[i])
            if i < len(archive_results):
                combined.append(archive_results[i])
        return combined[:top_k * 2]  # Limit total results
    else:
        # Just append archive results
        return current_results + archive_results[:top_k]

def mark_important(memory_text: str) -> bool:
    """
    Mark a specific memory as important so it won't be archived
    
    Returns:
        Boolean indicating success
    """
    memories = load_memory()
    
    # Try to find the memory by substring match
    memory_text = memory_text.lower()
    for memory in memories:
        if memory_text in memory.get("text", "").lower():
            # Found it - mark as important
            memory["important"] = True
            
            # Update in ChromaDB too if enabled
            if CHROMA_ENABLED:
                try:
                    # Generate the ID that would have been used when created
                    unique_id = f"{int(memory.get('timestamp', 0) * 1000)}"
                    
                    # Update ChromaDB metadata
                    memory_collection.update(
                        ids=[unique_id],
                        metadatas=[{"important": "true"}]  # Use string "true" for ChromaDB
                    )
                except Exception as e:
                    print(f"Error updating ChromaDB: {e}")
            
            # Save changes
            save_memory(memories)
            return True
    
    return False

def get_memory_health() -> Dict[str, Any]:
    """
    Get detailed health information about the memory system
    
    Returns:
        Dict with health metrics
    """
    # Basic stats
    memories = load_memory()
    total_memories = len(memories)
    
    if total_memories > 0:
        oldest_date = memories[0].get("date", "Unknown")
        newest_date = memories[-1].get("date", "Unknown")
    else:
        oldest_date = "N/A"
        newest_date = "N/A"
    
    file_size_kb = os.path.getsize(MEMORY_FILE) / 1024 if os.path.exists(MEMORY_FILE) else 0
    percent_full = (file_size_kb / MAX_FILE_SIZE_KB) * 100
    
    # Count important memories
    important_count = sum(1 for m in memories if m.get("important", False))
    
    # Check archive
    archive_files = []
    archived_memories = 0
    archive_size_kb = 0
    
    if os.path.exists(ARCHIVE_DIR):
        archive_files = [f for f in os.listdir(ARCHIVE_DIR) if f.startswith("memory_archive_")]
        for archive_file in archive_files:
            archive_path = os.path.join(ARCHIVE_DIR, archive_file)
            archive_size_kb += os.path.getsize(archive_path) / 1024
            try:
                with open(archive_path, 'r', encoding='utf-8') as f:
                    archived_memories += len(json.load(f).get("memories", []))
            except:
                pass
    
    # Return health data
    return {
        "active_memories": total_memories,
        "important_memories": important_count,
        "archived_memories": archived_memories,
        "total_memories": total_memories + archived_memories,
        "date_range": f"{oldest_date} to {newest_date}",
        "memory_file_size_kb": round(file_size_kb, 2),
        "memory_capacity_percent": round(percent_full, 1),
        "archive_enabled": os.path.exists(ARCHIVE_DIR),
        "archive_files": len(archive_files),
        "archive_size_kb": round(archive_size_kb, 2),
        "chromadb_enabled": CHROMA_ENABLED
    }

def memory_health_report() -> str:
    """Generate a human-readable health report for the memory system"""
    health = get_memory_health()
    
    report = []
    report.append("=== MEMORY SYSTEM HEALTH REPORT ===")
    report.append(f"Active memories: {health['active_memories']}")
    report.append(f"Important memories: {health['important_memories']}")
    report.append(f"Archived memories: {health['archived_memories']}")
    report.append(f"Total memories: {health['total_memories']}")
    report.append(f"Date range: {health['date_range']}")
    report.append(f"Memory file size: {health['memory_file_size_kb']}KB / {MAX_FILE_SIZE_KB}KB ({health['memory_capacity_percent']}%)")
    report.append(f"Archive status: {'Enabled' if health['archive_enabled'] else 'Not configured'}")
    report.append(f"Archive files: {health['archive_files']}")
    report.append(f"Archive size: {health['archive_size_kb']}KB")
    report.append(f"ChromaDB status: {'Active' if health['chromadb_enabled'] else 'Disabled'}")
    report.append("=================================")
    
    return "\n".join(report)

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--query" or command == "--recall":
            query = " ".join(sys.argv[2:])
            matches = query_memories(query)
            print(f"Top memory matches for: '{query}'\n")
            for m in matches:
                print("*", m)
                
        elif command == "--deep" or command == "--deep-search":
            query = " ".join(sys.argv[2:])
            matches = deep_search(query)
            print(f"Deep search results for: '{query}'\n")
            for m in matches:
                print("*", m)
                
        elif command == "--add" or command == "--remember":
            text = " ".join(sys.argv[2:])
            add_memory(text)
            print(f"Added new memory: '{text}'")
            
        elif command == "--important":
            text = " ".join(sys.argv[2:])
            add_memory(text, important=True)
            print(f"Added important memory: '{text}'")
            
        elif command == "--mark-important":
            text = " ".join(sys.argv[2:])
            success = mark_important(text)
            if success:
                print(f"Marked memory containing '{text}' as important")
            else:
                print(f"No memory found containing '{text}'")
                
        elif command == "--list":
            memories = load_memory()
            print(f"All memories ({len(memories)}):\n")
            for m in memories:
                imp = "[IMPORTANT] " if m.get("important", False) else ""
                print(f"* {imp}[{m['date']}] {m['text']}")
            
        elif command == "--health":
            print(memory_health_report())
            
        elif command == "--help":
            print("Claude Memory Manager - Available commands:")
            print("  --query <text>        Search for memories matching text")
            print("  --deep <text>         Deep search including archives")
            print("  --add <text>          Add a new memory")
            print("  --important <text>    Add an important memory (won't be archived)")
            print("  --mark-important <text> Mark existing memory as important")
            print("  --list                List all stored memories")
            print("  --health              Show memory system health report")
            print("  --help                Show this help message")
            
        else:
            print(f"Unknown command: {command}. Use --help for available commands.")
    else:
        print("Claude Memory Manager")
        print("Use --help for available commands")
