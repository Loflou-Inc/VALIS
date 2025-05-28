"""
Claude Memory Client

A simple client for interacting with the memory system.
Can be used as a standalone tool or integrated into other applications.
"""

import requests
import json
import os
import sys

class MemoryClient:
    """Client for interacting with the memory system"""
    
    def __init__(self, server_url="http://localhost:8080"):
        """Initialize the client with the server URL"""
        self.server_url = server_url
    
    def remember(self, text, important=False):
        """Add a new memory
        
        Args:
            text: The text to remember
            important: Whether this memory is important (won't be archived)
            
        Returns:
            Response object with success status
        """
        response = requests.post(
            f"{self.server_url}/remember",
            json={"text": text, "important": important}
        )
        return response.json()
    
    def query(self, query_text, top_k=5):
        """Query the memory system
        
        Args:
            query_text: The query to search for
            top_k: Number of results to return
            
        Returns:
            List of memory text strings
        """
        response = requests.get(
            f"{self.server_url}/query",
            params={"q": query_text, "top_k": top_k}
        )
        return response.json().get("memories", [])
    
    def deep_search(self, query_text, top_k=10, include_archives=True):
        """Perform a deep search including archives
        
        Args:
            query_text: The query to search for
            top_k: Number of results to return
            include_archives: Whether to include archived memories
            
        Returns:
            List of memory text strings
        """
        response = requests.get(
            f"{self.server_url}/deep",
            params={
                "q": query_text, 
                "top_k": top_k,
                "archives": "true" if include_archives else "false"
            }
        )
        return response.json().get("memories", [])
    
    def mark_important(self, text):
        """Mark an existing memory as important
        
        Args:
            text: Substring matching the memory to mark
            
        Returns:
            Response object with success status
        """
        response = requests.post(
            f"{self.server_url}/mark-important",
            json={"text": text}
        )
        return response.json()
    
    def get_health(self):
        """Get memory system health information
        
        Returns:
            Dict with health metrics
        """
        response = requests.get(f"{self.server_url}/health")
        return response.json()

def print_usage():
    """Print usage instructions for the command-line interface"""
    print("Claude Memory Client")
    print("Usage:")
    print("  python claude_memory_client.py remember <text>")
    print("  python claude_memory_client.py important <text>")
    print("  python claude_memory_client.py query <text> [top_k]")
    print("  python claude_memory_client.py deep <text> [top_k]")
    print("  python claude_memory_client.py mark <text>")
    print("  python claude_memory_client.py health")
    print("  python claude_memory_client.py help")

def main():
    """Main entry point for the command-line interface"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    # Get server URL from environment variable or use default
    server_url = os.environ.get("MEMORY_SERVER_URL", "http://localhost:8080")
    client = MemoryClient(server_url)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "remember":
            if len(sys.argv) < 3:
                print("Error: Missing memory text")
                return
            
            text = " ".join(sys.argv[2:])
            result = client.remember(text)
            print(f"Memory added: {result}")
            
        elif command == "important":
            if len(sys.argv) < 3:
                print("Error: Missing memory text")
                return
            
            text = " ".join(sys.argv[2:])
            result = client.remember(text, important=True)
            print(f"Important memory added: {result}")
            
        elif command == "query":
            if len(sys.argv) < 3:
                print("Error: Missing query text")
                return
            
            query = " ".join(sys.argv[2:-1]) if len(sys.argv) > 3 and sys.argv[-1].isdigit() else " ".join(sys.argv[2:])
            top_k = int(sys.argv[-1]) if len(sys.argv) > 3 and sys.argv[-1].isdigit() else 5
            
            memories = client.query(query, top_k=top_k)
            print(f"Query results for '{query}':")
            for i, memory in enumerate(memories, 1):
                print(f"{i}. {memory}")
            
        elif command == "deep":
            if len(sys.argv) < 3:
                print("Error: Missing query text")
                return
            
            query = " ".join(sys.argv[2:-1]) if len(sys.argv) > 3 and sys.argv[-1].isdigit() else " ".join(sys.argv[2:])
            top_k = int(sys.argv[-1]) if len(sys.argv) > 3 and sys.argv[-1].isdigit() else 10
            
            memories = client.deep_search(query, top_k=top_k)
            print(f"Deep search results for '{query}':")
            for i, memory in enumerate(memories, 1):
                print(f"{i}. {memory}")
            
        elif command == "mark":
            if len(sys.argv) < 3:
                print("Error: Missing memory text")
                return
            
            text = " ".join(sys.argv[2:])
            result = client.mark_important(text)
            
            if result.get("success", False):
                print(f"Successfully marked memory containing '{text}' as important")
            else:
                print(f"Failed to mark memory: {result}")
            
        elif command == "health":
            health = client.get_health()
            print("Memory System Health Report:")
            for key, value in health.items():
                print(f"  {key}: {value}")
            
        elif command == "help":
            print_usage()
            
        else:
            print(f"Unknown command: {command}")
            print_usage()
    
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to memory server at {server_url}")
        print("Make sure the server is running and the URL is correct.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
