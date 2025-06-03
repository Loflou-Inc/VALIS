import requests

# Test MCP backend on clean port 3004
r = requests.get("http://127.0.0.1:3004/api/health")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"MCP engine: {data.get('mcp_engine')}")
    print(f"External memory: {data.get('external_memory')}")
else:
    print(f"Error: {r.text[:100]}")
