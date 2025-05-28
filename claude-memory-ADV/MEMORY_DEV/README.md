# Claude Memory System

A lightweight, hybrid persistent memory system for Claude AI integrations.

## Overview

This memory system helps Claude maintain context across conversations by storing and retrieving memories based on semantic relevance. It uses a dual-backbone architecture:

1. **Flat-File Ledger (JSON)**: 
   - Stores all memories with timestamps and metadata
   - Human-readable and easily inspectable
   - Serves as the source of truth

2. **Vector Similarity Search (ChromaDB)**:
   - Generates embeddings for queries and memories
   - Uses cosine similarity to find relevant information
   - Falls back to simpler methods if advanced embeddings aren't available

## Features

- **Persistent Memory**: Maintains context across different chat sessions
- **Semantic Search**: Retrieves relevant memories based on query similarity
- **Tagging System**: Automatically tags memories with relevant categories
- **Importance Marking**: Special memories can be marked as important and won't be archived
- **Archiving**: Automatically archives older, less important memories to prevent the main file from growing too large
- **Health Monitoring**: Built-in system health reporting
- **Multiple Interfaces**: Command-line, API server, and direct library integration options
- **Simplified Scripts**: Dependency-free alternatives for basic memory operations

## Installation

1. Clone or download this repository
2. For full functionality with embeddings, install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. For basic functionality without dependencies, use the simplified scripts directly.
4. Initialize the system:
   ```
   python memory_manager.py --help
   ```

## Core Components

- **memory_manager.py**: Core memory system implementation
- **claude_integration.py**: Claude-specific integration functions
- **claude_dc_integration.py**: Desktop Commander interface for Claude
- **memory_server.py**: HTTP API server for remote access
- **claude_memory_client.py**: Client for interacting with the memory server
- **config.py**: Configuration settings
- **simple_read_memory.py**: Simplified memory reader with no dependencies
- **simple_update_memory.py**: Simplified memory writer with no dependencies

## Memory Directory Structure

```
MEMORY_DEV/
├── memory_manager.py        # Core memory system
├── claude_integration.py    # Claude-specific integration
├── claude_dc_integration.py # Desktop Commander integration
├── claude_memory_client.py  # Memory client
├── memory_server.py         # HTTP API server
├── config.py                # Configuration settings
├── simple_read_memory.py    # Simplified memory reader
├── simple_update_memory.py  # Simplified memory writer
├── read_memory.bat          # Batch file for reading memories
├── update_memory.bat        # Batch file for updating memories
├── start_server.bat         # Script to start the server
├── direct_start.bat         # Script to start server in console mode
├── requirements.txt         # Dependencies
├── README.md                # This file
└── memory_store/            # Memory storage directory
    ├── memories.json        # Main memory file
    ├── .chroma/             # ChromaDB storage (if enabled)
    └── archive/             # Archived memories
```

## Usage

### Quick Start with Batch Files

The simplest way to use the memory system is with the provided batch files:

```
# Read memories at the start of a conversation
read_memory.bat

# Add a new memory
update_memory.bat "Important information to remember"
```

These batch files automatically handle Python path detection and use the simplified scripts that don't require external dependencies.

### Advanced Usage in Python

```python
from memory_manager import add_memory, query_memories

# Add a memory
add_memory("The project uses Python and React for development.")

# Query memories
relevant_memories = query_memories("What technologies does the project use?", top_k=3)
print(relevant_memories)
```

### Desktop Commander Integration

For use with Claude's Desktop Commander:

```python
# Remember information
python claude_dc_integration.py remember "Project uses modular architecture."

# Recall information
python claude_dc_integration.py recall "architecture"

# Get memory context for Claude prompt
python claude_dc_integration.py context "How is the project designed?"

# List all memories
python claude_dc_integration.py list

# Check memory system health
python claude_dc_integration.py health
```

### HTTP API Server

Start the server:

```bash
python memory_server.py [port] [host]
# Default: localhost:8080
```

Or use the batch script:

```bash
start_server.bat
```

### Memory Client

Use the client to interact with the server:

```python
from claude_memory_client import MemoryClient

client = MemoryClient("http://localhost:8080")

# Add a memory
client.remember("User prefers dark mode in applications.", important=True)

# Query memories
results = client.query("user preferences")
print(results)
```

## Simplified Scripts

For environments where installing dependencies is challenging, use the simplified scripts:

```python
# Read memories without dependencies
python simple_read_memory.py

# Add a memory without dependencies
python simple_update_memory.py "Important information to remember"
```

These scripts provide basic memory functionality without requiring external libraries like sentence-transformers or ChromaDB.

## Claude Integration Instructions

To integrate with Claude conversations:

1. At the beginning of a chat, retrieve relevant context:
   ```python
   from claude_integration import get_memory_prompt
   
   user_input = "What were we working on last time?"
   memory_context = get_memory_prompt(user_input)
   
   # Include memory_context in Claude's prompt
   ```

2. At the end of a chat, store important information:
   ```python
   from claude_integration import process_conversation
   
   new_memory = process_conversation(user_input, claude_response)
   ```

3. Alternatively, Claude can directly trigger memory storage:
   ```python
   from claude_integration import auto_remember
   
   auto_remember("User is working on a new dashboard feature.")
   ```

## Best Practices

1. **Be Selective**: Only store truly important information that will be useful in future conversations
2. **Be Concise**: Keep memories short and to the point - ideally under 25 words
3. **Use Tagging**: The system automatically tags memories, but you can enhance this with descriptive content
4. **Mark Important**: Use the importance flag for critical information
5. **Regular Maintenance**: Occasionally check system health and prune unnecessary memories

## Technical Details

- **Embedding Model**: Uses sentence-transformers by default
- **Fallback Mechanism**: If advanced embedding methods aren't available, falls back to simple keyword matching
- **Deduplication**: Uses content hashing to prevent duplicate memories
- **Archiving**: Automatically archives older memories when the main file grows too large
- **Memory Format**: Each memory includes timestamp, text, embedding, tags, and importance flag

## Security and Privacy

- All memory data is stored locally in the memory_store directory
- No data is sent to external services
- Embeddings are generated locally when using sentence-transformers
- The system is designed to be transparent and inspectable
