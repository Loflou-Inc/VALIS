# Claude Memory System - Smart Version

This is an improved version of the memory system with stateful initialization to prevent repeated initialization loops.

## Key Improvements

1. **Stateful Initialization:**
   - The system now tracks when it has been initialized using `init_state.txt`
   - This prevents redundant initialization across session restarts

2. **Smart Scripts:**
   - `read_memory_smart.bat` - Checks if already initialized before reading memories
   - `update_memory_smart.bat` - Uses the improved smart update script
   - `smart_update_memory.py` - Intelligent memory management with duplicate detection

## How to Use

1. **Read Memories (at start of conversation):**
   ```
   G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\read_memory_smart.bat
   ```

2. **Update Memory (after important information):**
   ```
   G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\update_memory_smart.bat "MEMORY: Important information"
   ```

## File Structure

- `read_memory_smart.bat` - Initialize memory with state tracking
- `update_memory_smart.bat` - Update memory with new information
- `smart_update_memory.py` - Python script for updating memories
- `simple_read_memory.py` - Basic memory reading script
- `init_state.txt` - Tracks initialization state

## Backup

Redundant files have been moved to the `backup` directory. Do not use files from this directory.
