#!/usr/bin/env python3
"""
Simple QA Test Runner - Unicode Safe
Doc Brown's Temporal System Validation (Windows Compatible)
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

def test_basic_system_functionality():
    """Test basic VALIS system functionality without Unicode issues"""
    print("QA VALIDATION: Basic System Functionality Test")
    print("=" * 60)
    print("Doc Brown's Essential System Verification")
    print()
    
    test_results = []
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("Test 1: System Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get('status', 'unknown')
            providers = len(health_data.get('providers_available', []))
            print(f"  PASS: System Status: {status}, Providers: {providers}")
            test_results.append(("Health Check", True, f"Status: {status}, Providers: {providers}"))
        else:
            print(f"  FAIL: HTTP {response.status_code}")
            test_results.append(("Health Check", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"  FAIL: {e}")
        test_results.append(("Health Check", False, str(e)))
    
    # Test 2: Persona Loading
    print("\nTest 2: Persona Loading")
    try:
        response = requests.get(f"{base_url}/personas", timeout=10)
        if response.status_code == 200:
            personas = response.json()
            persona_count = len(personas)
            if persona_count > 0:
                persona_names = [p.get('name', 'Unknown') for p in personas[:3]]
                print(f"  PASS: Loaded {persona_count} personas: {', '.join(persona_names)}")
                test_results.append(("Persona Loading", True, f"{persona_count} personas loaded"))
            else:
                print(f"  FAIL: No personas loaded")
                test_results.append(("Persona Loading", False, "No personas loaded"))
        else:
            print(f"  FAIL: HTTP {response.status_code}")
            test_results.append(("Persona Loading", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"  FAIL: {e}")
        test_results.append(("Persona Loading", False, str(e)))
    
    # Test 3: Basic Chat Functionality
    print("\nTest 3: Basic Chat Functionality")
    try:
        chat_data = {
            "persona_id": "jane_thompson",
            "message": "Hello, this is a test message. Can you respond?",
            "session_id": f"test_session_{int(time.time())}"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=30)
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get('response', '')
            provider_used = response_data.get('provider_used', 'unknown')
            response_length = len(response_text)
            
            if response_length > 10:  # Basic sanity check
                print(f"  PASS: Response received ({response_length} chars) from {provider_used}")
                test_results.append(("Basic Chat", True, f"Provider: {provider_used}, Length: {response_length}"))
            else:
                print(f"  FAIL: Response too short ({response_length} chars)")
                test_results.append(("Basic Chat", False, f"Response too short: {response_length} chars"))
        else:
            print(f"  FAIL: HTTP {response.status_code}")
            test_results.append(("Basic Chat", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"  FAIL: {e}")
        test_results.append(("Basic Chat", False, str(e)))
    
    # Test 4: Configuration Access
    print("\nTest 4: Configuration Access")
    try:
        response = requests.get(f"{base_url}/config", timeout=10)
        if response.status_code == 200:
            config_data = response.json()
            providers_list = config_data.get('providers', [])
            provider_count = len(providers_list)
            print(f"  PASS: Config accessible, {provider_count} providers configured")
            test_results.append(("Configuration", True, f"{provider_count} providers configured"))
        else:
            print(f"  FAIL: HTTP {response.status_code}")
            test_results.append(("Configuration", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"  FAIL: {e}")
        test_results.append(("Configuration", False, str(e)))
    
    # Test 5: Sessions Endpoint
    print("\nTest 5: Sessions Management")
    try:
        response = requests.get(f"{base_url}/sessions", timeout=10)
        if response.status_code == 200:
            sessions_data = response.json()
            session_count = len(sessions_data)
            print(f"  PASS: Sessions endpoint accessible, {session_count} active sessions")
            test_results.append(("Sessions", True, f"{session_count} active sessions"))
        else:
            print(f"  FAIL: HTTP {response.status_code}")
            test_results.append(("Sessions", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"  FAIL: {e}")
        test_results.append(("Sessions", False, str(e)))
    
    # Generate Summary
    print("\n" + "=" * 60)
    print("QA VALIDATION SUMMARY:")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success, _ in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, success, details in test_results:
        status = "PASS" if success else "FAIL"
        print(f"  {status}: {test_name} - {details}")
    
    # Save results
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'success_rate': (passed_tests/total_tests)*100,
        'test_results': [
            {'test': name, 'success': success, 'details': details}
            for name, success, details in test_results
        ]
    }
    
    results_file = Path("C:/VALIS/simple_qa_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    if passed_tests == total_tests:
        print("\nVERDICT: BASIC SYSTEM VALIDATION PASSED!")
        print("Essential VALIS functionality is working correctly.")
        return True
    else:
        print("\nVERDICT: BASIC SYSTEM VALIDATION ISSUES DETECTED!")
        print("Some essential functionality may not be working properly.")
        return False

if __name__ == "__main__":
    test_basic_system_functionality()
