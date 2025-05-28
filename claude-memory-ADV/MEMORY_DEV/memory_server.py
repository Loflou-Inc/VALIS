"""
Claude Memory Server

Provides an HTTP API for accessing the memory system.
This allows for integration with other applications.
"""

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import traceback

# Add the parent directory to the path to import the memory_manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_manager import add_memory, query_memories, deep_search, mark_important, get_memory_health

class MemoryServer(BaseHTTPRequestHandler):
    """HTTP Server for the memory system"""
    
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Handle different endpoints
            if path == "/health":
                # Get memory system health
                health = get_memory_health()
                self._set_headers()
                self.wfile.write(json.dumps(health).encode())
                
            elif path == "/query":
                # Parse query parameters
                query_params = parse_qs(parsed_url.query)
                
                if "q" not in query_params:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing query parameter 'q'"}).encode())
                    return
                
                query = query_params["q"][0]
                top_k = int(query_params.get("top_k", [5])[0])
                
                # Get memories
                memories = query_memories(query, top_k=top_k)
                
                self._set_headers()
                self.wfile.write(json.dumps({"memories": memories}).encode())
                
            elif path == "/deep":
                # Parse query parameters
                query_params = parse_qs(parsed_url.query)
                
                if "q" not in query_params:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing query parameter 'q'"}).encode())
                    return
                
                query = query_params["q"][0]
                top_k = int(query_params.get("top_k", [10])[0])
                include_archives = query_params.get("archives", ["true"])[0].lower() == "true"
                
                # Get memories
                memories = deep_search(query, include_archives=include_archives, top_k=top_k)
                
                self._set_headers()
                self.wfile.write(json.dumps({"memories": memories}).encode())
                
            else:
                # 404 Not Found
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        
        except Exception as e:
            # Log the error
            print(f"Error handling GET request: {e}")
            traceback.print_exc()
            
            # Return a 500 error
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Get the request body length
            content_length = int(self.headers["Content-Length"])
            
            # Read the request body
            post_data = self.rfile.read(content_length).decode("utf-8")
            
            # Parse the JSON data
            data = json.loads(post_data)
            
            # Handle different endpoints
            if path == "/remember":
                # Check required parameters
                if "text" not in data:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing parameter 'text'"}).encode())
                    return
                
                text = data["text"]
                important = data.get("important", False)
                
                # Add memory
                add_memory(text, important=important)
                
                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "text": text}).encode())
                
            elif path == "/mark-important":
                # Check required parameters
                if "text" not in data:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing parameter 'text'"}).encode())
                    return
                
                text = data["text"]
                
                # Mark as important
                success = mark_important(text)
                
                self._set_headers()
                self.wfile.write(json.dumps({"success": success, "text": text}).encode())
                
            else:
                # 404 Not Found
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        
        except Exception as e:
            # Log the error
            print(f"Error handling POST request: {e}")
            traceback.print_exc()
            
            # Return a 500 error
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server(host="localhost", port=8080):
    """Run the memory server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, MemoryServer)
    print(f"Starting memory server on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    # Get host and port from command line arguments
    host = "localhost"
    port = 8080
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_server(host, port)
