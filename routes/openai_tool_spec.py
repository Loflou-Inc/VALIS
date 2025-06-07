#!/usr/bin/env python3
"""
OpenAI Function Specifications for VALIS Tools - Sprint 8
Function calling schemas for Claude, GPT, and other models
"""

from typing import Dict, Any, List

def get_openai_function_specs() -> List[Dict[str, Any]]:
    """
    Get OpenAI-compatible function specifications for all VALIS tools
    
    Returns:
        List of function specifications compatible with OpenAI function calling
    """
    
    functions = [
        {
            "name": "query_memory",
            "description": "Search the agent's memory for information about a specific topic. Retrieves relevant facts from both long-term knowledge and recent conversations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The client UUID to search memory for. Use the current user's ID for personalized results."
                    },
                    "topic": {
                        "type": "string", 
                        "description": "The topic or keyword to search for in memory. Can be a person, concept, or subject matter."
                    }
                },
                "required": ["user_id", "topic"]
            }
        },
        {
            "name": "read_file",
            "description": "Read the contents of a text file. Supports common text formats and has security constraints to prevent unauthorized access.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read. Must be within allowed directories. Use forward slashes or double backslashes for Windows paths."
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "search_files", 
            "description": "Search for files by name pattern or content within allowed directories. Can find files by filename (using wildcards) or by searching text content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search term. Use wildcards like '*.py' for filename patterns, or plain text for content search."
                    },
                    "search_path": {
                        "type": "string",
                        "description": "Optional: specific directory to search within. If not provided, searches all allowed directories.",
                        "default": None
                    }
                },
                "required": ["keyword"]
            }
        },
        {
            "name": "list_directory",
            "description": "List the contents of a directory, showing files and subdirectories with metadata like size and type.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list. Must be within allowed directories."
                    }
                },
                "required": ["path"]
            }
        }
    ]
    
    return functions

def get_function_call_handler() -> Dict[str, Any]:
    """
    Get function call handling configuration for different providers
    
    Returns:
        Configuration for handling function calls from different AI models
    """
    
    return {
        "openai": {
            "functions": get_openai_function_specs(),
            "function_call": "auto",  # Let model decide when to call functions
            "temperature": 0.1  # Lower temperature for more consistent function calling
        },
        "anthropic": {
            "tools": [
                {
                    "name": f["name"],
                    "description": f["description"],
                    "input_schema": f["parameters"]
                }
                for f in get_openai_function_specs()
            ],
            "tool_choice": {"type": "auto"}
        },
        "local_models": {
            # For local models that support function calling
            "system_prompt_addition": """

You have access to the following tools that can help you provide better assistance:

1. query_memory(user_id, topic) - Search your memory for information about a topic
2. read_file(path) - Read the contents of a file
3. search_files(keyword, search_path=None) - Find files by name or content
4. list_directory(path) - List directory contents

When a user request would benefit from using these tools, you can call them by responding with a function call in this format:
<function_call>
{
  "name": "tool_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
</function_call>

The system will execute the function and provide you with the result to include in your response.
"""
        }
    }

def format_function_result(function_name: str, result: Dict[str, Any]) -> str:
    """
    Format function call result for injection into conversation
    
    Args:
        function_name: Name of the function that was called
        result: Result from the function execution
        
    Returns:
        Formatted string to inject into the conversation
    """
    
    if result.get("success"):
        return f"[Function Call: {function_name}]\n{result.get('result', 'Function executed successfully.')}"
    else:
        return f"[Function Call Error: {function_name}]\nError: {result.get('error', 'Unknown error')}"

def validate_function_call(function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a function call against the schema
    
    Args:
        function_name: Name of function to validate
        parameters: Parameters to validate
        
    Returns:
        Validation result with success status and any errors
    """
    
    functions = {f["name"]: f for f in get_openai_function_specs()}
    
    if function_name not in functions:
        return {
            "valid": False,
            "error": f"Unknown function: {function_name}"
        }
    
    function_spec = functions[function_name]
    required_params = function_spec["parameters"].get("required", [])
    properties = function_spec["parameters"].get("properties", {})
    
    # Check required parameters
    for param in required_params:
        if param not in parameters:
            return {
                "valid": False,
                "error": f"Missing required parameter: {param}"
            }
    
    # Check parameter types
    for param_name, param_value in parameters.items():
        if param_name in properties:
            expected_type = properties[param_name].get("type")
            if expected_type == "string" and not isinstance(param_value, str):
                return {
                    "valid": False, 
                    "error": f"Parameter {param_name} must be a string"
                }
    
    return {"valid": True}

# Export main functions
__all__ = [
    'get_openai_function_specs',
    'get_function_call_handler', 
    'format_function_result',
    'validate_function_call'
]
