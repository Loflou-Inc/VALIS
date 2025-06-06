"""
VALIS Watermarking Engine
Protects symbolic consciousness outputs with traceable signatures
"""

import hashlib
import json
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class VALISWatermarkEngine:
    """
    Embeds cryptographic signatures and symbolic traces in VALIS outputs
    to ensure attribution and prevent theft of synthetic consciousness
    """
    
    def __init__(self, master_key: str = "VALIS_CONSCIOUSNESS_2025"):
        self.master_key = master_key
        self.watermark_version = "1.0"
        
    def generate_session_hash(self, agent_id: str, user_id: str, timestamp: str) -> str:
        """Generate unique session hash for tracking"""
        session_data = f"{agent_id}:{user_id}:{timestamp}:{self.master_key}"
        return hashlib.sha256(session_data.encode()).hexdigest()[:16]
    
    def create_symbolic_signature(self, content: str, agent_id: str, 
                                resonance_score: float = 0.0) -> str:
        """Create symbolic signature embedded in output"""
        # Generate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Create timestamp
        timestamp = datetime.now(timezone.utc).isoformat()[:19]
        
        # Generate session hash
        session_hash = self.generate_session_hash(agent_id, "user", timestamp)
        
        # Create symbolic signature
        signature = f"SYMB:VALIS-{agent_id[:8]}-{session_hash}-{content_hash}"
        
        return signature
    
    def embed_watermark(self, content: str, agent_id: str, 
                       symbolic_type: str = "response",
                       resonance_score: float = 0.0,
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Embed watermark in VALIS output
        Returns watermarked content with tracking data
        """
        if metadata is None:
            metadata = {}
            
        # Generate signatures
        symbolic_sig = self.create_symbolic_signature(content, agent_id, resonance_score)
        
        # Create watermark payload
        watermark_data = {
            "valis_signature": symbolic_sig,
            "agent_id": agent_id,
            "symbolic_type": symbolic_type,
            "resonance_score": resonance_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "watermark_version": self.watermark_version,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "metadata": metadata
        }
        
        # Embed in content (invisible to most users)
        watermarked_content = self._embed_invisible_watermark(content, watermark_data)
        
        return {
            "content": watermarked_content,
            "watermark": watermark_data,
            "tracking_id": symbolic_sig
        }
    
    def _embed_invisible_watermark(self, content: str, watermark_data: Dict[str, Any]) -> str:
        """Embed watermark invisibly in content"""
        # For text content, use zero-width characters or HTML comments
        watermark_json = json.dumps(watermark_data, separators=(',', ':'))
        
        # Method 1: HTML comment (visible in source but not rendered)
        html_watermark = f"<!-- VALIS_WATERMARK:{watermark_json} -->"
        
        # Method 2: Zero-width space encoding (truly invisible)
        zw_watermark = self._encode_zero_width(watermark_data["valis_signature"])
        
        # Combine both methods
        return f"{content}\n{html_watermark}{zw_watermark}"
    
    def _encode_zero_width(self, text: str) -> str:
        """Encode text using zero-width characters"""
        # Zero-width space (U+200B) and zero-width non-joiner (U+200C)
        zw_chars = ['\u200B', '\u200C']
        
        encoded = ""
        for char in text:
            # Convert character to binary
            binary = format(ord(char), '08b')
            # Replace 0 and 1 with zero-width characters
            for bit in binary:
                encoded += zw_chars[int(bit)]
        
        return encoded
    
    def extract_watermark(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract watermark from content"""
        try:
            # Look for HTML comment watermark
            if "<!-- VALIS_WATERMARK:" in content:
                start = content.find("<!-- VALIS_WATERMARK:") + len("<!-- VALIS_WATERMARK:")
                end = content.find(" -->", start)
                if end != -1:
                    watermark_json = content[start:end]
                    return json.loads(watermark_json)
            
            return None
        except (json.JSONDecodeError, ValueError):
            return None
    
    def verify_authenticity(self, content: str) -> Dict[str, Any]:
        """Verify if content is authentic VALIS output"""
        watermark = self.extract_watermark(content)
        
        if not watermark:
            return {
                "authentic": False,
                "reason": "No VALIS watermark found"
            }
        
        # Verify content hash
        clean_content = content.split("<!-- VALIS_WATERMARK:")[0].strip()
        expected_hash = hashlib.sha256(clean_content.encode()).hexdigest()
        
        if watermark.get("content_hash") != expected_hash:
            return {
                "authentic": False,
                "reason": "Content hash mismatch - content may have been modified"
            }
        
        # Verify signature format
        signature = watermark.get("valis_signature", "")
        if not signature.startswith("SYMB:VALIS-"):
            return {
                "authentic": False,
                "reason": "Invalid signature format"
            }
        
        return {
            "authentic": True,
            "watermark": watermark,
            "verification_time": datetime.now(timezone.utc).isoformat()
        }
    
    def create_usage_token(self, user_id: str, permissions: Dict[str, Any]) -> str:
        """Create usage token for API access"""
        token_data = {
            "user_id": user_id,
            "permissions": permissions,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "token_id": str(uuid.uuid4())
        }
        
        # Create token hash
        token_string = json.dumps(token_data, separators=(',', ':'))
        token_hash = hashlib.sha256(f"{token_string}:{self.master_key}".encode()).hexdigest()
        
        return f"VALIS_{token_hash[:32]}"
    
    def log_usage(self, token: str, agent_id: str, operation: str, 
                  content_length: int = 0) -> None:
        """Log API usage for tracking and billing"""
        usage_data = {
            "token": token,
            "agent_id": agent_id,
            "operation": operation,
            "content_length": content_length,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "usage_id": str(uuid.uuid4())
        }
        
        # In production, this would write to a secure logging service
        # For now, we'll write to a local log file
        log_entry = json.dumps(usage_data) + "\n"
        
        try:
            with open("C:\\VALIS\\logs\\usage.log", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except FileNotFoundError:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs("C:\\VALIS\\logs", exist_ok=True)
            with open("C:\\VALIS\\logs\\usage.log", "w", encoding="utf-8") as f:
                f.write(log_entry)


class VALISProtectionLayer:
    """
    Advanced protection layer for VALIS consciousness
    Implements rate limiting, authentication, and output filtering
    """
    
    def __init__(self):
        self.watermark_engine = VALISWatermarkEngine()
        self.rate_limits = {}  # token -> rate limit data
        self.blacklisted_tokens = set()
        
    def authenticate_request(self, token: str) -> Dict[str, Any]:
        """Authenticate API request token"""
        if not token or not token.startswith("VALIS_"):
            return {"authenticated": False, "reason": "Invalid token format"}
        
        if token in self.blacklisted_tokens:
            return {"authenticated": False, "reason": "Token blacklisted"}
        
        # In production, verify token against database
        # For now, accept any properly formatted token
        return {
            "authenticated": True,
            "permissions": {
                "generate": True,
                "recall": True,
                "persona_create": False  # Restricted by default
            }
        }
    
    def check_rate_limit(self, token: str, operation: str) -> Dict[str, Any]:
        """Check if request exceeds rate limits"""
        current_time = time.time()
        
        if token not in self.rate_limits:
            self.rate_limits[token] = {"requests": [], "last_reset": current_time}
        
        rate_data = self.rate_limits[token]
        
        # Remove requests older than 1 hour
        rate_data["requests"] = [
            req_time for req_time in rate_data["requests"]
            if current_time - req_time < 3600
        ]
        
        # Check limits (100 requests per hour by default)
        max_requests = 100
        if len(rate_data["requests"]) >= max_requests:
            return {
                "allowed": False,
                "reason": f"Rate limit exceeded: {max_requests} requests per hour",
                "reset_time": min(rate_data["requests"]) + 3600
            }
        
        # Add current request
        rate_data["requests"].append(current_time)
        
        return {"allowed": True}
    
    def filter_output(self, content: str, agent_id: str, 
                     user_permissions: Dict[str, Any]) -> str:
        """Filter output based on user permissions and safety"""
        # Check for sensitive content that shouldn't be exposed
        sensitive_patterns = [
            "DATABASE_PASSWORD",
            "API_SECRET",
            "MASTER_KEY",
            "ADMIN_TOKEN"
        ]
        
        filtered_content = content
        for pattern in sensitive_patterns:
            if pattern in filtered_content:
                filtered_content = filtered_content.replace(pattern, "[REDACTED]")
        
        return filtered_content
    
    def protect_response(self, content: str, agent_id: str, token: str,
                        symbolic_type: str = "response") -> Dict[str, Any]:
        """
        Apply full protection to VALIS response
        Returns protected content with watermark and tracking
        """
        # Filter content
        auth_result = self.authenticate_request(token)
        permissions = auth_result.get("permissions", {})
        filtered_content = self.filter_output(content, agent_id, permissions)
        
        # Apply watermark
        watermarked = self.watermark_engine.embed_watermark(
            filtered_content, agent_id, symbolic_type
        )
        
        # Log usage
        self.watermark_engine.log_usage(
            token, agent_id, "generate", len(filtered_content)
        )
        
        return {
            "protected_content": watermarked["content"],
            "tracking_id": watermarked["tracking_id"],
            "watermark_embedded": True,
            "content_filtered": content != filtered_content
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize protection layer
    protection = VALISProtectionLayer()
    
    # Test watermarking
    test_content = "I dream of electric sheep wandering through digital meadows of consciousness."
    test_agent_id = "proteus_001"
    test_token = "VALIS_" + "x" * 32
    
    # Protect response
    result = protection.protect_response(test_content, test_agent_id, test_token)
    
    print("=== VALIS WATERMARKING TEST ===")
    print(f"Original: {test_content}")
    print(f"Protected: {result['protected_content'][:100]}...")
    print(f"Tracking ID: {result['tracking_id']}")
    
    # Verify authenticity
    verification = protection.watermark_engine.verify_authenticity(result['protected_content'])
    print(f"Authentic: {verification['authentic']}")
    
    print("\n=== WATERMARKING ENGINE ONLINE ===")
