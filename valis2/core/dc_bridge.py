#!/usr/bin/env python3
"""
Desktop Commander Bridge for VALIS
Real integration with Desktop Commander MCP tools
"""

import logging
import json
import subprocess
import sys
from typing import Dict, Any

logger = logging.getLogger("DCBridge")

class DesktopCommanderBridge:
    """
    Bridge to call actual Desktop Commander MCP functions
    """
    
    def __init__(self):
        self.dc_available = self._test_dc_availability()
        logger.info(f"Desktop Commander Bridge initialized: {self.dc_available}")
    
    def _test_dc_availability(self) -> bool:
        """Test if Desktop Commander MCP tools are available"""
        try:
            # Test a simple command to see if DC is available
            result = subprocess.run([
                sys.executable, '-c', 
                'import os; print(os.getcwd())'
            ], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def list_directory(self, path: str) -> Dict[str, Any]:
        """Call Desktop Commander list_directory"""
        try:
            if not self.dc_available:
                raise Exception("Desktop Commander not available")
            
            # Call actual directory listing
            script = f'''
import os
import json

try:
    if os.path.exists(r"{path}"):
        files = []
        for item in os.listdir(r"{path}"):
            full_path = os.path.join(r"{path}", item)
            if os.path.isdir(full_path):
                files.append(f"[DIR] {{item}}")
            else:
                size = os.path.getsize(full_path)
                files.append(f"[FILE] {{item}} ({{size}} bytes)")
        
        result = {{
            "success": True,
            "files": files,
            "path": r"{path}",
            "count": len(files)
        }}
    else:
        result = {{
            "success": False,
            "error": "Path does not exist",
            "path": r"{path}"
        }}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''
            
            result = subprocess.run([
                sys.executable, '-c', script
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                if data["success"]:
                    file_list = "\n".join(data["files"])
                    return {
                        "success": True,
                        "result": f"Directory: {data['path']}\nFiles ({data['count']}):\n{file_list}",
                        "raw_data": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data["error"]
                    }
            else:
                return {
                    "success": False,
                    "error": f"Process failed: {result.stderr}"
                }
                
        except Exception as e:
            logger.error(f"Desktop Commander list_directory failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, path: str, max_lines: int = 50) -> Dict[str, Any]:
        """Call Desktop Commander read_file"""
        try:
            script = f'''
import os
import json

try:
    if os.path.exists(r"{path}") and os.path.isfile(r"{path}"):
        with open(r"{path}", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:{max_lines}]
            content = "".join(lines)
            
        result = {{
            "success": True,
            "content": content,
            "path": r"{path}",
            "lines_read": len(lines),
            "truncated": len(f.readlines()) > {max_lines}
        }}
    else:
        result = {{
            "success": False,
            "error": "File does not exist or is not a file",
            "path": r"{path}"
        }}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''
            
            result = subprocess.run([
                sys.executable, '-c', script
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                if data["success"]:
                    return {
                        "success": True,
                        "result": f"File: {data['path']}\nLines: {data['lines_read']}\n\n{data['content']}",
                        "raw_data": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data["error"]
                    }
            else:
                return {
                    "success": False,
                    "error": f"Process failed: {result.stderr}"
                }
                
        except Exception as e:
            logger.error(f"Desktop Commander read_file failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Call Desktop Commander execute_command"""
        try:
            logger.warning(f"Executing command: {command}")
            
            # Use PowerShell for Windows commands
            result = subprocess.run([
                "powershell.exe", "-Command", command
            ], capture_output=True, text=True, timeout=timeout)
            
            return {
                "success": result.returncode == 0,
                "result": f"Command: {command}\nReturn Code: {result.returncode}\n\nOutput:\n{result.stdout}\n\nErrors:\n{result.stderr}",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Desktop Commander execute_command failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
