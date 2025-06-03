import requests
import json

base_url = "http://127.0.0.1:3004"

print("=== MCP VALIS SYSTEM TEST ===")

# 1. Health check
r = requests.get(f"{base_url}/api/health")
print(f"Health: {r.status_code} - MCP: {r.json()['mcp_engine']}")

# 2. Available personas
r = requests.get(f"{base_url}/api/personas")
personas = r.json()
print(f"Personas: {len(personas)} available")

# 3. Memory status for Jane
r = requests.get(f"{base_url}/api/memory/status/jane")
print(f"Memory status: {r.status_code}")

# 4. Initialize Jane
r = requests.get(f"{base_url}/api/persona/initialize/jane")
init_data = r.json()
print(f"Jane init: Ready={init_data['ready']}, Memory={init_data['memory_loaded']}")

# 5. Dev command - memory status
dev_payload = {"command": "memory_status", "persona_id": "jane"}
r = requests.post(f"{base_url}/api/dev/command", json=dev_payload)
print(f"Dev command: {r.status_code}")

# 6. Chat test with minimal prompt
chat_payload = {
    "persona": "jane",
    "message": "Hi Jane, can you help me with a team communication issue?",
    "client_id": "test_client",
    "session_id": "test_session_1"
}
r = requests.post(f"{base_url}/api/chat", json=chat_payload)
chat_data = r.json()
print(f"Chat: {r.status_code}")
print(f"External memory: {chat_data['external_memory']}")
print(f"Prompt length: {chat_data['prompt_length']} chars")
print(f"Response preview: {chat_data['response'][:100]}...")

print("\n=== TEST COMPLETE ===")
