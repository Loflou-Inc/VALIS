import requests
import json

payload = {
    "persona": "jane",
    "message": "Hi Jane, I'm having trouble with my team not listening to me in meetings. What should I do?",
    "client_id": "test_client",
    "session_id": "test_session_1"
}

r = requests.post("http://127.0.0.1:3001/api/chat", json=payload)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"Response: {data.get('response', 'No response')}")
else:
    print(f"Error: {r.text}")
