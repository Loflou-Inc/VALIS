#!/usr/bin/env python3
import requests

# Test root endpoint
try:
    r = requests.get("http://127.0.0.1:3001/")
    print(f"Root endpoint status: {r.status_code}")
    print(f"Content type: {r.headers.get('content-type', 'unknown')}")
    print(f"Content length: {len(r.text)} bytes")
    if 'html' in r.headers.get('content-type', ''):
        print("HTML content detected - frontend is loading")
    else:
        print("Response content preview:")
        print(r.text[:200])
except Exception as e:
    print(f"Failed to connect: {e}")
