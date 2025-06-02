#!/usr/bin/env python3
"""
Direct MCP Communication Test
Test the MCP server communication directly
"""

import asyncio
import json
import sys

async def test_mcp_communication():
    """Test direct MCP communication"""
    
    print("Starting MCP communication test...")
    
    try:
        # Start MCP server process
        process = await asyncio.create_subprocess_exec(
            "python", "C:/VALIS/mcp_server/valis_persona_mcp_server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("MCP process started successfully")
        
        # Send initialize message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        
        print(f"Sending initialize message: {json.dumps(init_msg)}")
        
        process.stdin.write((json.dumps(init_msg) + "\n").encode())
        await process.stdin.drain()
        
        print("Initialize message sent, waiting for response...")
        
        # Wait for response with timeout
        try:
            response_data = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            print(f"Raw response: {response_data}")
            
            if response_data:
                response_text = response_data.decode().strip()
                print(f"Response text: {response_text}")
                
                response = json.loads(response_text)
                print(f"Parsed response: {json.dumps(response, indent=2)}")
                
                if "result" in response:
                    print("SUCCESS: Got valid initialize response!")
                else:
                    print(f"ERROR: Invalid response format")
            else:
                print("ERROR: No response received")
                
        except asyncio.TimeoutError:
            print("ERROR: Timeout waiting for response")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
        
        # Check stderr for any errors
        stderr_data = await process.stderr.read()
        if stderr_data:
            print(f"STDERR: {stderr_data.decode()}")
        
        # Clean up
        process.terminate()
        await process.wait()
        print("Process terminated")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_communication())
