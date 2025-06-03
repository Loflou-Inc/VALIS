#!/usr/bin/env python3
"""
VALIS System Launcher - Windows Compatible (NO UNICODE)
Emergency Temporal Repair Version
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_status(message):
    """Print status without Unicode characters"""
    print(f"[VALIS] {message}")

def check_prerequisites():
    """Check that all required files exist"""
    print_status("Checking system prerequisites...")
    
    valis_dir = Path("C:/VALIS")
    required_files = [
        "start_enhanced_api_server.py",
        "config.json",
        ".env"
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = valis_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print_status(f"MISSING REQUIRED FILES: {missing_files}")
        return False
    
    print_status("Prerequisites check: PASSED")
    return True

def start_enhanced_api_server():
    """Start the VALIS enhanced API server"""
    print_status("Starting VALIS Enhanced API Server...")
    
    try:
        # Change to VALIS directory
        os.chdir("C:/VALIS")
        
        # Start the server
        process = subprocess.Popen(
            [sys.executable, "start_enhanced_api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("API Server started successfully")
            print_status("Server available at: http://localhost:8000")
            print_status("API Documentation: http://localhost:8000/docs")
            return process
        else:
            print_status("API Server failed to start")
            return None
            
    except Exception as e:
        print_status(f"Error starting API server: {e}")
        return None

def test_api_health():
    """Test if the API is responding"""
    print_status("Testing API health...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get('status', 'unknown')
            providers = len(health_data.get('providers_available', []))
            print_status(f"API Health: {status}, Providers: {providers}")
            return True
        else:
            print_status(f"API Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_status(f"API Health check error: {e}")
        return False

def launch_valis_system():
    """Launch the complete VALIS system"""
    print_status("=" * 60)
    print_status("VALIS SYSTEM LAUNCHER")
    print_status("Emergency Temporal Repair Launch Protocol")
    print_status("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print_status("Prerequisites check failed - aborting launch")
        return False
    
    # Start API server
    server_process = start_enhanced_api_server()
    if not server_process:
        print_status("Failed to start API server - aborting launch")
        return False
    
    # Wait for server to be ready
    print_status("Waiting for server to be ready...")
    time.sleep(5)
    
    # Test API health
    if not test_api_health():
        print_status("API health check failed")
        server_process.terminate()
        return False
    
    print_status("=" * 60)
    print_status("VALIS SYSTEM LAUNCH: SUCCESS")
    print_status("API Backend: http://localhost:8000")
    print_status("Health Check: http://localhost:8000/health")
    print_status("API Docs: http://localhost:8000/docs")
    print_status("=" * 60)
    print_status("System is ready for democratizing AI access!")
    print_status("Press Ctrl+C to stop the system")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if server process is still alive
            if server_process.poll() is not None:
                print_status("Server process died unexpectedly")
                break
    except KeyboardInterrupt:
        print_status("Shutting down VALIS system...")
        server_process.terminate()
        try:
            server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print_status("VALIS system shutdown complete")
    
    return True

if __name__ == "__main__":
    success = launch_valis_system()
    sys.exit(0 if success else 1)
