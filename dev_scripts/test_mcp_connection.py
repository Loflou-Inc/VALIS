#!/usr/bin/env python3
"""
VALIS MCP Connection Diagnostic Tool
Tests the persistent MCP server connection and verifies JSON-RPC communication
This replaces brittle stdout parsing with proper structured testing
"""

import asyncio
import json
import sys
import argparse
import time
from pathlib import Path

class MCPDiagnostic:
    """Diagnostic tool for testing MCP server connection"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.test_results = []
        
    async def test_connection(self) -> bool:
        """Test basic TCP connection to MCP server"""
        print(f"[TEST] Connecting to MCP server at {self.host}:{self.port}...")
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5.0
            )
            
            writer.close()
            await writer.wait_closed()
            
            print("[PASS] Connection successful")
            self.test_results.append("Connection: PASS")
            return True
            
        except Exception as e:
            print(f"[FAIL] Connection failed: {e}")
            self.test_results.append(f"Connection: FAIL ({e})")
            return False
    
    async def test_ping(self) -> bool:
        """Test ping method to verify server is responding"""
        print("[TEST] Testing ping method...")
        
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            ping_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "ping",
                "params": {}
            }
            
            writer.write((json.dumps(ping_msg) + '\n').encode('utf-8'))
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.readline(), timeout=5.0)
            response = json.loads(response_data.decode('utf-8').strip())
            
            writer.close()
            await writer.wait_closed()
            
            if "result" in response and response["result"].get("status") == "alive":
                print("[PASS] Ping successful")
                print(f"  Server status: {response['result']}")
                self.test_results.append("Ping: PASS")
                return True
            else:
                print(f"[FAIL] Ping failed: {response}")
                self.test_results.append(f"Ping: FAIL")
                return False
                
        except Exception as e:
            print(f"[FAIL] Ping failed: {e}")
            self.test_results.append(f"Ping: FAIL ({e})")
            return False
    
    async def test_persona_request(self, persona_id="jane", message="Hello, how are you?") -> bool:
        """Test a complete persona request/response cycle"""
        print(f"[TEST] Testing persona request for '{persona_id}'...")
        
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            request_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "ask_persona",
                "params": {
                    "persona_id": persona_id,
                    "message": message,
                    "context": {}
                }
            }
            
            writer.write((json.dumps(request_msg) + '\n').encode('utf-8'))
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.readline(), timeout=10.0)
            response = json.loads(response_data.decode('utf-8').strip())
            
            writer.close()
            await writer.wait_closed()
            
            if "result" in response:
                result = response["result"]
                print("[PASS] Persona request successful")
                print(f"  Persona: {result.get('persona_name', 'Unknown')}")
                print(f"  Response: {result.get('response', 'No response')[:100]}...")
                self.test_results.append(f"Persona ({persona_id}): PASS")
                return True
            else:
                print(f"[FAIL] Persona request failed: {response}")
                self.test_results.append(f"Persona ({persona_id}): FAIL")
                return False
                
        except Exception as e:
            print(f"[FAIL] Persona request failed: {e}")
            self.test_results.append(f"Persona ({persona_id}): FAIL ({e})")
            return False
    
    async def run_all_tests(self):
        """Run complete diagnostic suite"""
        print("=== VALIS MCP Connection Diagnostic ===")
        print(f"Target: {self.host}:{self.port}")
        print()
        
        # Test 1: Basic connection
        if not await self.test_connection():
            print("\n[ERROR] Basic connection failed - server may not be running")
            return
        
        # Test 2: Ping
        if not await self.test_ping():
            print("\n[ERROR] Server not responding to ping")
            return
        
        # Test 3: Persona requests
        personas_to_test = ["jane", "emma", "billy", "alex", "sam"]
        for persona in personas_to_test:
            await self.test_persona_request(persona, f"Hello from {persona} test!")
            await asyncio.sleep(0.5)  # Small delay between tests
        
        # Summary
        print("\n=== TEST SUMMARY ===")
        for result in self.test_results:
            print(f"  {result}")
        
        passed = len([r for r in self.test_results if "PASS" in r])
        total = len(self.test_results)
        print(f"\nResult: {passed}/{total} tests passed")
        
        if passed == total:
            print("[SUCCESS] All tests passed! MCP integration is working correctly.")
        else:
            print("[WARNING] Some tests failed. Check MCP server status.")


async def main():
    """Main entry point for diagnostic tool"""
    parser = argparse.ArgumentParser(description='VALIS MCP Connection Diagnostic')
    parser.add_argument('--host', default='localhost', help='MCP server host')
    parser.add_argument('--port', type=int, default=8765, help='MCP server port')
    parser.add_argument('--persona', help='Test specific persona only')
    parser.add_argument('--message', help='Custom test message')
    
    args = parser.parse_args()
    
    diagnostic = MCPDiagnostic(args.host, args.port)
    
    if args.persona:
        # Test specific persona
        test_message = args.message or f"Hello from {args.persona} diagnostic test!"
        await diagnostic.test_connection()
        await diagnostic.test_ping()
        await diagnostic.test_persona_request(args.persona, test_message)
    else:
        # Run full diagnostic suite
        await diagnostic.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nDiagnostic error: {e}")
        sys.exit(1)
