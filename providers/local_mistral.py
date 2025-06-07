#!/usr/bin/env python3
"""
LocalMistralProvider - HTTP client to local Mistral server
Simple provider that sends requests to localhost:8080
"""

import requests
import logging
import time
from typing import Dict, Any

logger = logging.getLogger("LocalMistralProvider")

class LocalMistralProvider:
    """Local Mistral 7B provider via llama.cpp server"""
    
    def __init__(self):
        self.api_url = "http://localhost:8080/completion"
        self.timeout = 30
        logger.info("🤖 LocalMistralProvider initialized")
    
    def ask(self, prompt: str, client_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Send prompt to local Mistral server
        
        Returns:
        {
            "success": bool,
            "response": str,
            "error": str (if failed),
            "latency": float,
            "tokens": int
        }
        """
        
        start_time = time.time()
        
        # Compose JSON payload
        payload = {
            "prompt": prompt,
            "n_predict": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop": ["User:", "Assistant:"]
        }
        
        try:
            logger.info(f"Calling local Mistral: {len(prompt)} chars")
            
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=self.timeout
            )
            
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("content", "").strip()
                
                logger.info(f"✓ Success: {latency:.2f}s")
                
                return {
                    "success": True,
                    "response": response_text,
                    "latency": latency,
                    "tokens": len(response_text) // 4  # Rough estimate
                }
            else:
                error = f"HTTP {response.status_code}"
                logger.error(f"✗ Server error: {error}")
                
                return {
                    "success": False,
                    "error": error,
                    "latency": latency
                }
                
        except requests.exceptions.Timeout:
            latency = time.time() - start_time
            logger.error(f"✗ Timeout after {latency:.2f}s")
            
            return {
                "success": False,
                "error": "Request timeout",
                "latency": latency
            }
            
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"✗ Exception: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "latency": latency
            }
