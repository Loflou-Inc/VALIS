#!/usr/bin/env python3
"""
Function-Calling Provider Base - Sprint 8 Phase 3
Base class for providers that support function calling with tools
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import sys
import os
from pathlib import Path

# Add valis2 to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.tool_manager import tool_manager
from api.openai_tool_spec import get_openai_function_specs, format_function_result, validate_function_call

logger = logging.getLogger("FunctionCallingProvider")

class FunctionCallingProvider(ABC):
    """
    Base class for AI providers that support function calling
    Handles tool integration, function call detection, and result injection
    """
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.available_functions = {f["name"]: f for f in get_openai_function_specs()}
        logger.info(f"{provider_name} FunctionCallingProvider initialized with {len(self.available_functions)} tools")
    
    @abstractmethod
    def _call_api(self, prompt: str, client_id: str, persona_id: str, 
                  functions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the underlying AI API (Claude, GPT, etc.)
        
        Args:
            prompt: User prompt
            client_id: Client UUID
            persona_id: Persona UUID  
            functions: Available functions for function calling
            
        Returns:
            API response with content and any function calls
        """
        pass
    
    def ask(self, prompt: str, client_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Main provider interface with function calling support
        
        Args:
            prompt: User prompt
            client_id: Client UUID
            persona_id: Persona UUID
            
        Returns:
            Response with function call results integrated
        """
        try:
            # Prepare function specifications for the model
            functions = list(self.available_functions.values())
            
            # Call the underlying API
            api_response = self._call_api(prompt, client_id, persona_id, functions)
            
            if not api_response.get("success"):
                return api_response
            
            # Check if the response contains function calls
            function_calls = self._extract_function_calls(api_response)
            
            if function_calls:
                # Execute function calls and integrate results
                return self._handle_function_calls(function_calls, prompt, client_id, persona_id, api_response)
            else:
                # No function calls, return normal response
                return {
                    "success": True,
                    "response": api_response.get("content", ""),
                    "provider": self.provider_name,
                    "metadata": api_response.get("metadata", {})
                }
                
        except Exception as e:
            logger.error(f"{self.provider_name} provider error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_name
            }
    
    def _extract_function_calls(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract function calls from API response
        Handles different function calling formats from different providers
        """
        function_calls = []
        
        # Check for OpenAI-style function calls
        if "function_call" in api_response:
            function_calls.append(api_response["function_call"])
        elif "tool_calls" in api_response:
            function_calls.extend(api_response["tool_calls"])
        
        # Check for function calls in content (for models that embed them in text)
        content = api_response.get("content", "")
        if "<function_call>" in content:
            embedded_calls = self._parse_embedded_function_calls(content)
            function_calls.extend(embedded_calls)
        
        return function_calls
    
    def _parse_embedded_function_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse function calls embedded in text content"""
        function_calls = []
        
        # Look for <function_call>...</function_call> blocks
        pattern = r'<function_call>\s*(\{.*?\})\s*</function_call>'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                call_data = json.loads(match.group(1))
                if "name" in call_data and "parameters" in call_data:
                    function_calls.append({
                        "function": {
                            "name": call_data["name"],
                            "arguments": json.dumps(call_data["parameters"])
                        }
                    })
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse embedded function call: {match.group(1)}")
        
        return function_calls
    
    def _handle_function_calls(self, function_calls: List[Dict[str, Any]], 
                              original_prompt: str, client_id: str, persona_id: str,
                              api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute function calls and integrate results into response
        """
        try:
            function_results = []
            
            for call in function_calls:
                # Extract function name and arguments 
                if "function" in call:
                    func_name = call["function"]["name"]
                    func_args = json.loads(call["function"]["arguments"])
                elif "name" in call:
                    func_name = call["name"] 
                    func_args = call.get("parameters", {})
                else:
                    continue
                
                # Validate function call
                validation = validate_function_call(func_name, func_args)
                if not validation["valid"]:
                    function_results.append({
                        "function": func_name,
                        "error": validation["error"]
                    })
                    continue
                
                # Execute function via ToolManager
                logger.info(f"Executing function call: {func_name} with args: {func_args}")
                
                result = tool_manager.execute_tool(
                    tool_name=func_name,
                    parameters=func_args,
                    client_id=client_id,
                    persona_id=persona_id
                )
                
                function_results.append({
                    "function": func_name,
                    "result": result,
                    "formatted": format_function_result(func_name, result)
                })
            
            # Integrate function results into response
            original_content = api_response.get("content", "")
            
            # Remove function call tags from content if they exist
            clean_content = re.sub(r'<function_call>.*?</function_call>', '', original_content, flags=re.DOTALL)
            clean_content = clean_content.strip()
            
            # Combine original response with function results
            if function_results:
                result_text = "\n\n".join([fr["formatted"] for fr in function_results])
                
                if clean_content:
                    final_response = f"{clean_content}\n\n{result_text}"
                else:
                    final_response = result_text
            else:
                final_response = clean_content or "Function calls completed."
            
            return {
                "success": True,
                "response": final_response,
                "provider": self.provider_name,
                "metadata": {
                    **api_response.get("metadata", {}),
                    "function_calls": len(function_calls),
                    "function_results": [{"function": fr["function"], "success": fr["result"].get("success")} for fr in function_results]
                }
            }
            
        except Exception as e:
            logger.error(f"Function call handling failed: {e}")
            return {
                "success": False,
                "error": f"Function call execution failed: {str(e)}",
                "provider": self.provider_name
            }


class MockClaudeProvider(FunctionCallingProvider):
    """
    Mock Claude provider for testing function calling
    (Replace with real Anthropic API integration)
    """
    
    def __init__(self):
        super().__init__("claude_mock")
    
    def _call_api(self, prompt: str, client_id: str, persona_id: str, 
                  functions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock Claude API call with function calling simulation"""
        
        # Simulate Claude deciding to call a function based on prompt
        if "list files" in prompt.lower() or "directory" in prompt.lower():
            return {
                "success": True,
                "content": "I'll help you list the directory contents.",
                "function_call": {
                    "function": {
                        "name": "list_directory", 
                        "arguments": json.dumps({"path": "C:\\VALIS"})
                    }
                }
            }
        elif "read file" in prompt.lower():
            return {
                "success": True,
                "content": "I'll read that file for you.",
                "function_call": {
                    "function": {
                        "name": "read_file",
                        "arguments": json.dumps({"path": "C:\\VALIS\\README.md"})
                    }
                }
            }
        elif "what do you know" in prompt.lower() or "remember" in prompt.lower():
            return {
                "success": True,
                "content": "Let me search my memory for that information.",
                "function_call": {
                    "function": {
                        "name": "query_memory",
                        "arguments": json.dumps({"user_id": client_id, "topic": "general"})
                    }
                }
            }
        else:
            return {
                "success": True,
                "content": f"I understand your request: {prompt}. I'm a mock Claude provider for testing.",
                "metadata": {"model": "claude-mock", "tokens": len(prompt.split())}
            }
