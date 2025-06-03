# VALIS Developer Scripts

> 🛠️ **Developer tools, diagnostics, and local test scripts**

This folder contains tools for debugging providers, personas, and interface issues. These are **not used in production** but help during development and troubleshooting.

## 📋 Available Tools

### **MCP Integration Testing**
#### `test_mcp_connection.py`
**Purpose**: Tests persistent MCP server connection and verifies JSON-RPC communication  
**Usage**: 
```bash
python dev_scripts/test_mcp_connection.py
python dev_scripts/test_mcp_connection.py --port 8766
```
**Expected Output**:
```
=== VALIS MCP Connection Diagnostic ===
[PASS] Connection successful
[PASS] Ping successful
Result: 7/7 tests passed
[SUCCESS] All tests passed! MCP integration is working correctly.
```
**Requirements**: MCP server must be running (`python mcp_server/valis_persona_mcp_server_persistent.py`)

### **End-to-End Integration Testing**
#### `test_valis_persistent_integration.py`
**Purpose**: Tests complete VALIS engine with persistent MCP provider  
**Usage**:
```bash
python dev_scripts/test_valis_persistent_integration.py
```
**Expected Output**:
```
[PASS] VALIS engine initialized
[PASS] jane -> Desktop Commander MCP (Persistent)
[SUCCESS] Persistent MCP integration working!
```
**Requirements**: MCP server running, VALIS config pointing to persistent provider

### **Provider Validation**
#### `validate_providers.py`
**Purpose**: Validates all registered providers implement correct interfaces  
**Usage**:
```bash
python dev_scripts/validate_providers.py
```
**Expected Output**:
```
=== Provider Validation - Sprint 2 ===
Found 4 registered providers: ['desktop_commander_mcp_persistent', 'hardcoded_fallback', 'anthropic_api', 'openai_api']
desktop_commander_mcp_persistent: 2/2 tests passed
hardcoded_fallback: 2/2 tests passed
Overall: 6/8 tests passed
```
**Requirements**: None (validates interface compliance)

### **Deployment Validation**
#### `validate_deployment.py`
**Purpose**: Validates VALIS deployment and environment setup
**Usage**:
```bash
python dev_scripts/validate_deployment.py
```
**Expected Output**: Environment check and dependency validation
**Requirements**: None (environment validation)

#### `simple_deployment_check.py`
**Purpose**: Quick deployment status check
**Usage**:
```bash
python dev_scripts/simple_deployment_check.py
```
**Expected Output**: Basic system status
**Requirements**: None (simple health check)

## 🚀 Running Tests

### Quick Validation Workflow
```bash
# 1. Start MCP server (in separate terminal)
python mcp_server/valis_persona_mcp_server_persistent.py --debug

# 2. Test MCP connection
python dev_scripts/test_mcp_connection.py

# 3. Test full integration
python dev_scripts/test_valis_persistent_integration.py

# 4. Validate all providers
python dev_scripts/validate_providers.py
```

## 📝 Notes

- All tools use relative paths and work from VALIS root directory
- Tools are designed to be cross-platform (Windows/Linux/macOS)
- For production deployment testing, see `docs/setup/` instead
- Legacy test scripts moved to `tests/legacy/` during Sprint 4 cleanup
- Test result files (`.json` outputs) are kept here for reference

## 📊 Test Results Archive

This folder also contains test result files from validation runs:
- `cascade_test_results.json` - Provider cascade test results
- `simple_qa_validation_results.json` - QA validation test results

---
**Sprint 4**: Developer tools organized and documented for clear dev experience.
