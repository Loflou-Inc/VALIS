import requests
import json

# Test MCP backend
print("Testing MCP Backend...")

# Health check
r = requests.get("http://127.0.0.1:3001/api/health")
print(f"Health: {r.status_code} - {r.json()}")

# Memory status
r = requests.get("http://127.0.0.1:3001/api/memory/status/jane")
print(f"Memory status: {r.status_code}")

# Initialize persona
r = requests.get("http://127.0.0.1:3001/api/persona/initialize/jane")
print(f"Initialize Jane: {r.status_code} - Ready: {r.json()['ready']}")

# Dev command
payload = {"command": "memory_status", "persona_id": "jane"}
r = requests.post("http://127.0.0.1:3001/api/dev/command", json=payload)
print(f"Dev command: {r.status_code}")

# Chat test
chat_payload = {
    "persona": "jane",
    "message": "Hello Jane",
    "client_id": "test_client",
    "session_id": "test_session"
}
r = requests.post("http://127.0.0.1:3001/api/chat", json=chat_payload)
print(f"Chat: {r.status_code} - External memory: {r.json().get('external_memory')}")
print(f"Prompt length: {r.json().get('prompt_length')} chars")
