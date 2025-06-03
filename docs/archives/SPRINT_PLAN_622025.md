# 🔧 VALIS Sprint Plan – MCP Fixes, Provider Cleanup, Dev Clarity

**Sprint Duration:** 2 Weeks  
**Priority:** High – Unblock Claude MCP integration, remove developer confusion, stabilize core pipeline

---

## 🧭 Sprint 1: MCP Claude Integration Rework

**🎯 Goal:**  
Replace fragile subprocess bridge with persistent Claude MCP JSON-RPC service.

### ✅ Tasks

- Refactor `valis_persona_mcp_server.py` to run as a persistent process.
- Modify `RealDesktopCommanderMCPProvider`:
  - Maintain long-lived connection (pipe, socket, or persistent subprocess)
  - Use structured JSON-RPC for each message
  - Eliminate `"Claude:"` and `"FALLBACK_RESPONSE_JSON"` parsing
- Allow clean fallback if Claude clone is not available
- Add CLI test script: `test_mcp_connection.py`

### ✅ Acceptance Criteria

- MCP provider stable across multiple chats
- JSON structure is respected
- Fallback triggers only when MCP truly offline
- Diagnostic CLI test works reliably

---

## 🧭 Sprint 2: Provider System Cleanup

**🎯 Goal:**  
Consolidate provider system to remove dead code and ensure clarity.

### ✅ Tasks

- Remove or archive `desktop_commander_provider.py`
- Ensure `provider_registry.py` cleanly imports real MCP provider
- Validate fallback, Anthropic, and OpenAI implementations
- Confirm all providers follow unified interface (`get_response()` etc.)

### ✅ Acceptance Criteria

- No confusion between real/fake Claude providers
- Fallback logic modular and opt-in
- Registry is source of truth for all providers

---

## 🧭 Sprint 3: Documentation Update & Dev Clarity

**🎯 Goal:**  
Ensure developers know how to run, debug, and integrate VALIS.

### ✅ Tasks

- Rewrite `CLAUDE_CLONE_SETUP.md`:
  - Describe new persistent interface
  - Add simple run example
- Add `CONFIGURATION.md`:
  - Cover `.env`, timeouts, persona dirs, fallback toggles
- Move old md files (tests, logs) → `docs/archives/`
- Tag deprecated code with `# DEPRECATED` and pointer

### ✅ Acceptance Criteria

- Claude setup is crystal clear
- No misleading documentation in root
- Markdown/docs all reflect stable state

---

## 🧭 Sprint 4: Repo Cleanup & Dev Usability

**🎯 Goal:**  
Make the codebase clear, navigable, and clean of legacy/test clutter.

### ✅ Tasks

- Move test/dev scripts → `dev_scripts/`
- Add `README.md` to explain usage of each dev tool
- Delete broken/unmaintained test scripts
- Standardize paths: no more `C:/VALIS`
- Add `docs/` folder for current and future system docs

### ✅ Acceptance Criteria

- Root folder contains only real project entrypoints
- Dev scripts isolated
- No Windows-specific hardcoding or test-only logic in core

---

## 🌀 Next Sprints (Post-Cleanup)

- Full MCP function/memory hook
- Persona config UI/editor
- Provider test suite
- Dashboard & diagnostics UI

---

📁 Save this file as `VALIS
