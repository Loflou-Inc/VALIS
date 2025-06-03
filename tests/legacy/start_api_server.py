#!/usr/bin/env python3
"""
VALIS API Server Startup Script
Temporal-Safe AI Democratization Service
"""

import uvicorn
import os
from pathlib import Path

def start_valis_api():
    """Start the VALIS API server with optimal configuration"""
    
    print("STARTING VALIS API SERVER")
    print("=" * 50)
    print("Temporal-Safe AI Democratization Service")
    print("Doc Brown's Specifications Implemented")
    print("FastAPI + VALIS Engine Integration")
    print("-" * 50)
    
    # Ensure we're in the right directory
    valis_dir = Path(__file__).parent
    os.chdir(valis_dir)
    
    print(f"Working Directory: {valis_dir}")
    print("Starting server on http://localhost:8000")
    print("Available endpoints:")
    print("   POST /chat - Chat with personas")
    print("   GET  /personas - List available personas")
    print("   GET  /sessions - View active sessions")
    print("   GET  /health - System health check")
    print("   GET  /config - View configuration")
    print("   POST /config - Update configuration")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "valis_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_valis_api()
