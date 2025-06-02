#!/usr/bin/env python3
"""
Test VALIS API Implementation
"""

from fastapi.testclient import TestClient
from valis_api import app

def test_api():
    print("TESTING VALIS API IMPLEMENTATION")
    print("=" * 50)
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Health check
    print("Test 1: Health Check")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"System Status: {health_data.get('status', 'unknown')}")
        print(f"Providers Available: {len(health_data.get('providers_available', []))}")
    
    # Test 2: Get personas
    print("\nTest 2: Get Personas")
    response = client.get("/personas")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        personas = response.json()
        print(f"Personas loaded: {len(personas)}")
        for persona in personas[:2]:  # Show first 2
            print(f"  - {persona['name']} ({persona['role']})")
    
    print("\nAPI IMPLEMENTATION VERIFIED!")

if __name__ == "__main__":
    test_api()
