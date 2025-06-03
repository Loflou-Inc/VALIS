#!/usr/bin/env python3
"""
VALIS Professional Development Setup
Runs the Flask backend and serves the React frontend in development mode
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_backend():
    """Run the Flask backend"""
    print("Starting VALIS Backend API...")
    backend_process = subprocess.Popen([
        sys.executable, "backend.py", "--port", "3001", "--debug"
    ], cwd=Path(__file__).parent)
    return backend_process

def run_frontend():
    """Run the React development server"""
    print("Starting React Frontend Development Server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Create a custom vite config that proxies API calls to our backend
    vite_config = """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
"""
    
    # Write the vite config
    vite_config_path = frontend_dir / "vite.config.ts"
    with open(vite_config_path, 'w') as f:
        f.write(vite_config)
    
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir)
    return frontend_process

def main():
    """Main development server launcher"""
    print("=" * 60)
    print("VALIS PROFESSIONAL DEVELOPMENT SETUP")
    print("=" * 60)
    print()
    print("This will start:")
    print("- Flask Backend API on http://127.0.0.1:3001")
    print("- React Frontend Dev Server on http://127.0.0.1:3000")
    print("- Frontend will proxy /api requests to backend")
    print()
    print("Press Ctrl+C to stop both servers")
    print()
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = run_backend()
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = run_frontend()
        
        print()
        print("=" * 60)
        print("SERVERS RUNNING!")
        print("=" * 60)
        print("Frontend: http://127.0.0.1:3000")
        print("Backend API: http://127.0.0.1:3001/api")
        print("Backend Health: http://127.0.0.1:3001/api/health")
        print()
        print("Press Ctrl+C to stop...")
        print()
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("Backend process died!")
                break
            if frontend_process.poll() is not None:
                print("Frontend process died!")
                break
                
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        
    finally:
        # Clean up processes
        if backend_process:
            try:
                backend_process.terminate()
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                
        if frontend_process:
            try:
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
        
        print("Servers stopped.")

if __name__ == "__main__":
    main()
