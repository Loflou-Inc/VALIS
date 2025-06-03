# VALIS Claude Integration Setup Guide

> ⚠️ **NOTE**: This document applies to the **new persistent MCP interface only** (Sprint 1 implementation).
> For legacy documentation, see `docs/archives/`

## 🎯 Overview

VALIS integrates with Claude Desktop via a **persistent JSON-RPC server** for reliable persona responses. This setup eliminates subprocess spawning and provides structured communication.

## 🏗️ Architecture

```
[VALIS Engine] 
    ↓ (JSON-RPC over TCP)
[Persistent MCP Server] ← Long-running Python process
    ↓ (Persona responses)
[Claude Desktop] ← Optional enhanced integration
```

**Key Benefits:**
- ✅ No subprocess spawning per request
- ✅ Structured JSON communication  
- ✅ Persistent connection with session handling
- ✅ Clean error handling and fallbacks
- ✅ Enterprise-ready reliability

## 🚀 Quick Start

### 1. Start the Persistent MCP Server

```bash
# Navigate to VALIS directory
cd /path/to/VALIS

# Start the persistent server (default port 8766)
python mcp_server/valis_persona_mcp_server_persistent.py --debug
```

### 2. Test the Connection

```bash
# Run the diagnostic tool
python test_mcp_connection.py

# Expected output:
# [PASS] Connection successful
# [PASS] Ping successful  
# Result: 7/7 tests passed
```

### 3. Test VALIS Integration

```bash
# Test end-to-end with VALIS engine
python test_valis_persistent_integration.py

# Expected output:
# [PASS] jane -> Desktop Commander MCP (Persistent)
# [SUCCESS] Persistent MCP integration working!
```

## 📡 JSON-RPC Protocol

### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "ask_persona",
  "params": {
    "persona_id": "jane",
    "message": "How do I handle team conflict?",
    "context": {}
  }
}
```

### Response Format
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "result": {
    "response": "Hi! As an HR professional, I can help you work through this workplace challenge...",
    "provider": "valis_persistent_mcp",
    "persona_id": "jane",
    "persona_name": "Jane Thompson"
  }
}
```

## ⚙️ Configuration

### Server Options
```bash
# Custom port
python valis_persona_mcp_server_persistent.py --port 8888

# Debug logging
python valis_persona_mcp_server_persistent.py --debug
```

### VALIS Provider Configuration
Update `config.json`:
```json
{
  "providers": ["desktop_commander_mcp_persistent", "anthropic_api", "openai_api", "hardcoded_fallback"]
}
```

The persistent provider will automatically:
- Connect to `localhost:8766` (configurable)
- Fall back gracefully if server unavailable
- Log all connection attempts and failures

## 🔧 Troubleshooting

### Connection Issues
**Problem**: "MCP server availability check failed"
**Solution**: Ensure the persistent server is running on the correct port

**Problem**: "Connection refused"  
**Solution**: Check Windows firewall or try a different port

### Provider Issues
**Problem**: VALIS uses fallback instead of MCP
**Solution**: Check provider order in `config.json`

**Problem**: Persona responses are generic
**Solution**: Verify persona JSON files are loaded correctly

### Getting Help
- Run diagnostics: `python test_mcp_connection.py`
- Check logs for detailed error messages
- Verify provider validation: `python validate_providers.py`

## 📚 Additional Resources

- **Provider Development**: See `PROVIDER_DEVELOPMENT_GUIDE.md`
- **Configuration**: See `CONFIGURATION.md` 
- **Legacy Setup**: See `docs/archives/CLAUDE_CLONE_SETUP.md` (deprecated)

---
**Sprint 3 Documentation Update**: This guide replaces all legacy Claude integration instructions.
