# VALIS Claude Desktop MCP Setup Instructions

## Overview
VALIS uses a "Clone Claude" architecture where a second Claude Desktop instance acts as an MCP server for persona responses.

## Architecture
```
[Development Claude (This one)] ← Used for building VALIS
[VALIS Platform] → [Provider Cascade] → [Clone Claude MCP Server] → [Real Persona Responses]
```

## Setup Steps

### 1. Set up Clone Claude Desktop Instance

**Option A: Second User Account (Recommended)**
1. Create a new Windows user account for the "Clone Claude"
2. Install Claude Desktop on that account
3. Configure the MCP server (see step 2)

**Option B: Same User, Different Profile**
1. Create a portable Claude Desktop installation
2. Use different config directory

### 2. Configure Clone Claude MCP Server

Copy this config to Clone Claude's config directory:
**Location:** `C:\Users\[USER]\AppData\Roaming\Claude\claude_desktop_config.json`

**Content:** (Use the file at `C:\VALIS\mcp_server\claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "valis-persona-server": {
      "command": "python",
      "args": ["C:\\VALIS\\mcp_server\\valis_persona_mcp_server.py"],
      "env": {}
    }
  }
}
```

### 3. Start Clone Claude Desktop
1. Launch the second Claude Desktop instance
2. Verify "valis-persona-server" appears in Tools/MCP servers
3. The clone is now ready to respond as VALIS personas

### 4. Test VALIS Connection
1. Start VALIS backend: `python valis_api.py`
2. Start VALIS frontend: `npm run dev` (in frontend directory)
3. Open dashboard at `http://localhost:3001`
4. Try chat with any persona
5. Should see "Desktop Commander MCP" as provider (not fallback)

## How It Works

1. User sends message via VALIS dashboard
2. VALIS tries Desktop Commander MCP provider first
3. Provider connects to Clone Claude MCP server
4. Clone Claude gets persona context prompt
5. Clone Claude responds AS that persona
6. Response flows back to VALIS dashboard

## Troubleshooting

**MCP Connection Failed:**
- Check Clone Claude Desktop is running
- Verify MCP server config is correct
- Check Windows firewall settings
- VALIS will fallback to basic persona responses

**Clone Claude Not Loading MCP Server:**
- Verify Python is in PATH
- Check file paths in config are correct
- Look at Clone Claude's error logs

## Files Created
- `C:\VALIS\mcp_server\valis_persona_mcp_server.py` - MCP server for Clone Claude
- `C:\VALIS\mcp_server\claude_desktop_config.json` - Config for Clone Claude
- `C:\VALIS\providers\desktop_commander_mcp_real.py` - Real MCP client for VALIS

## Result
✅ VALIS gets real Claude persona responses through proper MCP architecture
✅ No API keys required
✅ Full Claude intelligence for each persona
✅ Clean separation: Dev Claude vs Persona Claude
