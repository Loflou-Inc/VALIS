# How to Use the Claude Memory System

This guide provides practical examples for integrating the memory system into your Claude experience.

## Quick Start

1. **With Batch Files (No Dependencies Required)**
   ```
   read_memory.bat
   update_memory.bat "Important information to remember"
   ```

2. **With Full System (Requires Dependencies)**
   ```
   pip install -r requirements.txt
   python test_memory.py
   ```

## Simplified Usage (No Dependencies)

For basic memory functionality without installing any dependencies:

```
# Read all memories
python simple_read_memory.py

# Add a new memory
python simple_update_memory.py "Important information to remember"
```

These simplified scripts provide core memory functionality and work without external libraries.

## Desktop Commander Integration

The most common way to use the memory system with Claude Desktop Commander:

### Remembering Information

When Claude learns something important that should be remembered for future sessions:

```
python F:\MEMORY_DEV\claude_dc_integration.py remember "User prefers minimalist design with dark color schemes."
```

For especially important information that should never be archived:

```
python F:\MEMORY_DEV\claude_dc_integration.py important "User's name is Alex Thompson and they work as a UX designer."
```

### Recalling Information

At the start of a conversation, recall relevant context:

```
python F:\MEMORY_DEV\claude_dc_integration.py recall "design preferences"
```

For a more comprehensive search including archived memories:

```
python F:\MEMORY_DEV\claude_dc_integration.py deep "design preferences"
```

### Getting Context for Claude

The most useful command - creates a formatted context block for Claude:

```
python F:\MEMORY_DEV\claude_dc_integration.py context "What was the project we were working on?"
```

This will output a formatted memory context block that Claude can read and incorporate into its response without explicitly mentioning that it's using memories.

### Memory Management

List all stored memories:

```
python F:\MEMORY_DEV\claude_dc_integration.py list
```

Check system health:

```
python F:\MEMORY_DEV\claude_dc_integration.py health
```

Mark existing memory as important:

```
python F:\MEMORY_DEV\claude_dc_integration.py mark "design preferences"
```

## Recommended Workflow with Claude

1. **Start of conversation**:
   ```
   read_memory.bat
   ```
   This provides Claude with all memories from previous conversations.

2. **During conversation**: If Claude learns something important, it should automatically remember the information:
   ```
   update_memory.bat "MEMORY: User is working on a dashboard redesign due next Friday."
   ```

3. **For specific topics**: When the conversation shifts to a specific topic, get targeted context:
   ```
   python F:\MEMORY_DEV\claude_dc_integration.py context "dashboard project"
   ```

4. **After conversation**: Review stored memories occasionally:
   ```
   python F:\MEMORY_DEV\claude_dc_integration.py list
   ```

## Automation with Claude

Claude can be set up to automatically use the memory system by:

1. Running `read_memory.bat` at the start of each conversation
2. Running `update_memory.bat "MEMORY: Key information"` after each substantive response
3. Incorporating memory information naturally without explicit references

This automation should be included in Claude's system prompt for seamless memory integration.

## Using the HTTP Server

For more advanced integrations, you can use the HTTP server:

1. **Start the server**:
   ```
   F:\MEMORY_DEV\start_server.bat
   ```

2. **Use the client**:
   ```python
   from claude_memory_client import MemoryClient
   
   client = MemoryClient("http://localhost:8080")
   client.remember("Implemented new feature X")
   results = client.query("feature implementation")
   ```

3. **Direct API access**:
   - `GET /query?q=search+term&top_k=5`
   - `GET /deep?q=search+term&top_k=10&archives=true`
   - `GET /health`
   - `POST /remember` with JSON body `{"text": "memory text", "important": false}`
   - `POST /mark-important` with JSON body `{"text": "memory substring"}`

## Tips for Effective Memory Use

1. **Be specific** with memory text - avoid vague statements
2. **Start with action verbs** when possible (e.g., "Created", "Implemented", "Fixed")
3. **Keep it concise** - under 25 words is ideal
4. **Use consistent terminology** to improve search results
5. **Mark truly important** information that should never be archived
6. **Clean up occasionally** by archiving old memories

## Troubleshooting

- If you encounter dependency issues, use the simplified scripts (`simple_read_memory.py` and `simple_update_memory.py`)
- If ChromaDB initialization fails, the system will continue to work with the flat-file backend only
- If memory retrieval returns unexpected results, try the deep search option
- Check system health to monitor memory usage and potential issues
- The `memory_store` directory contains all data - back it up occasionally
