#!/usr/bin/env python3
"""
VALIS Enhanced API Server Startup Script
Doc Brown's API-102 & API-103 Implementation
Temporal-Safe AI Democratization Service with Message History
"""

import uvicorn
import os
from pathlib import Path

def start_enhanced_valis_api():
    """Start the Enhanced VALIS API server with all temporal safeguards"""
    
    print("STARTING ENHANCED VALIS API SERVER")
    print("=" * 60)
    print("Temporal-Safe AI Democratization Service")
    print("Doc Brown's API-102 & API-103 Specifications")
    print("FastAPI + VALIS Engine + Message History Integration")
    print("All Temporal Disaster Prevention Safeguards Active")
    print("-" * 60)
    
    # Ensure we're in the right directory
    valis_dir = Path(__file__).parent
    os.chdir(valis_dir)
    
    print(f"Working Directory: {valis_dir}")
    print("Starting server on http://localhost:3313")
    print("Enhanced endpoints:")
    print("   POST /chat - Chat with personas + message history")
    print("   GET  /personas - List available personas") 
    print("   GET  /sessions - View active sessions + message counts")
    print("   GET  /sessions/{id}/history - View session message history")
    print("   GET  /health - System health + message history stats")
    print("   GET  /config - View configuration")
    print("   POST /config - Update configuration")
    print("   GET  /admin/stats - System monitoring statistics")
    print("-" * 60)
    print("TEMPORAL SAFEGUARDS ACTIVE:")
    print("   Secure JSON logging (API keys filtered)")
    print("   CORS localhost:3000 for development")
    print("   Message history with auto-cleanup (24h)")
    print("   Max 100 messages per session")
    print("   Global message limit: 10,000")
    print("   SQLite database with proper indexing")
    print("   Privacy-safe data handling")
    print("-" * 60)
    print("Interactive API docs: http://localhost:3313/docs")
    print("Alternative docs: http://localhost:3313/redoc")
    print("-" * 60)
    
    # Start the enhanced server with Doc Brown's configuration
    uvicorn.run(
        "valis_api:app",
        host="0.0.0.0",
        port=3313,
        reload=True,
        access_log=True,
        log_level="debug",  # Enhanced debug logging (API-102)
        use_colors=True,
        reload_dirs=["./"]
    )

if __name__ == "__main__":
    start_enhanced_valis_api()
