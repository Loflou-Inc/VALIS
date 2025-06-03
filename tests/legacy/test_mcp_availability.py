#!/usr/bin/env python3
"""
Test script to debug MCP provider availability check
"""
import asyncio
from pathlib import Path

async def test_mcp_availability():
    """Test the exact logic used in DesktopCommanderProvider.is_available()"""
    
    # Same path logic as the provider
    mcp_interface_path = Path(__file__).parent / "mcp_integration" / "dc_persona_interface.py"
    print(f"Testing MCP interface at: {mcp_interface_path}")
    
    # Check if file exists
    if not mcp_interface_path.exists():
        print(f"ERROR: MCP interface script does not exist!")
        return False
    
    print(f"File exists: {mcp_interface_path.exists()}")
    
    try:
        # Exact subprocess call from the provider
        process = await asyncio.create_subprocess_exec(
            "python", str(mcp_interface_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("Subprocess created, waiting for output...")
        
        # Wait for completion with timeout (same as provider)
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            
            print(f"Process return code: {process.returncode}")
            print(f"Output length: {len(output)}")
            print(f"Output: {repr(output)}")
            
            # Same availability logic as provider
            has_usage = "Usage:" in output
            has_error = "error" in output
            result = has_usage or has_error
            
            print(f"Contains 'Usage:': {has_usage}")
            print(f"Contains 'error:': {has_error}")
            print(f"Availability result: {result}")
            
            return result
            
        except asyncio.TimeoutError:
            print("TIMEOUT: Process took longer than 5 seconds")
            process.kill()
            await process.wait()
            return False
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mcp_availability())
    print(f"\nFINAL RESULT: {result}")
