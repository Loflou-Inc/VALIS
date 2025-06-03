# VALIS Configuration Guide

> 📋 **Single Source of Truth**: All configurable parameters and settings for VALIS

## 📄 Main Configuration (`config.json`)

### Core Settings
```json
{
  "providers": ["desktop_commander_mcp_persistent", "anthropic_api", "openai_api", "hardcoded_fallback"],
  "logging_level": "INFO",
  "enable_memory": true
}
```

### Performance Settings
```json
{
  "performance": {
    "max_concurrent_requests": 10,
    "provider_timeout": 30,
    "circuit_breaker": {
      "failure_threshold": 3,
      "timeout_minutes": 5
    }
  }
}
```

### Feature Flags
```json
{
  "features": {
    "enable_neural_health_monitor": true,
    "enable_circuit_breaker": true,
    "enable_retry_logic": true
  }
}
```

## 🔧 Environment Variables

```bash
# Core settings
VALIS_PROVIDERS=desktop_commander_mcp_persistent,anthropic_api,hardcoded_fallback
VALIS_LOG_LEVEL=INFO
VALIS_PERSONAS_DIR=personas
```

# MCP settings
VALIS_MCP_HOST=localhost
VALIS_MCP_PORT=8766
VALIS_MCP_TIMEOUT=30

# API keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## 🎯 Provider Configuration

### Provider Order (Fallback Cascade)
1. **desktop_commander_mcp_persistent** - Persistent MCP (FREE)
2. **anthropic_api** - Anthropic Claude API (PAID)
3. **openai_api** - OpenAI GPT API (PAID)
4. **hardcoded_fallback** - Static responses (FREE)

### Sample .env File
```bash
# VALIS Configuration
VALIS_PROVIDERS=desktop_commander_mcp_persistent,anthropic_api,hardcoded_fallback
VALIS_LOG_LEVEL=INFO
VALIS_PERSONAS_DIR=personas
VALIS_MCP_PORT=8766

# API Keys (optional)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## 📊 Logging Configuration

### Log Levels
- `DEBUG` - Detailed diagnostic information
- `INFO` - General operational messages  
- `WARNING` - Warning messages
- `ERROR` - Error conditions

### Log Destinations
- **Console** - Standard output (default)
- **File** - `valis_api.log` (when running API server)
- **Memory system** - Important events stored in memory

## 🚀 Quick Configuration

### Development Setup
```json
{
  "providers": ["desktop_commander_mcp_persistent", "hardcoded_fallback"],
  "logging_level": "DEBUG",
  "enable_memory": true
}
```

### Production Setup  
```json
{
  "providers": ["anthropic_api", "openai_api", "hardcoded_fallback"],
  "logging_level": "INFO",
  "enable_memory": true,
  "performance": {
    "max_concurrent_requests": 50,
    "provider_timeout": 30
  }
}
```

---
**Sprint 3 Documentation**: Complete configuration reference for all VALIS settings.
