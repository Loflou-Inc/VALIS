import requests

# Test MCP backend on port 3002
r = requests.get("http://127.0.0.1:3002/api/health")
print(f"MCP Health: {r.status_code}")
data = r.json()
print(f"MCP engine: {data.get('mcp_engine')}")
print(f"External memory: {data.get('external_memory')}")
