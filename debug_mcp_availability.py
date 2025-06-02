#!/usr/bin/env python3
"""
Debug MCP Availability Check
Tests the exact same subprocess call that DesktopCommanderProvider uses
"""

import asyncio
import subprocess
from pathlib import Path

async def test_mcp_availability():
    """Test the exact availability check from DesktopCommanderProvider"""
    
    mcp_interface_path = Path(__file__).parent / "mcp_integration" / "dc_persona_interface.py"
    
    print(f"Testing MCP interface at: {mcp_interface_path}")
    print(f"File exists: {mcp_interface_path.exists()}")
    
    try:
        # This is the EXACT same code from DesktopCommanderProvider.is_available()
        process = await asyncio.create_subprocess_exec(
            "python", str(mcp_interface_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            
            print(f"Process return code: {process.returncode}")
            print(f"STDOUT: {stdout.decode('utf-8')}")
            print(f"STDERR: {stderr.decode('utf-8')}")
            print(f"Combined output: {output}")
            
            # Check the availability condition
            available = "Usage:" in output or "error" in output
            print(f"Availability check result: {available}")
            
            return available
            
        except asyncio.TimeoutError:
            print("TIMEOUT ERROR - Process took too long!")
            process.kill()
            await process.wait()
            return False
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mcp_availability())
    print(f"Final result: {result}")
