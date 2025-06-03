#!/usr/bin/env python3
"""
VALIS Complete System Launcher
Starts both Enhanced API Backend and React Frontend
Doc Brown's Full Democratization Platform
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import signal
import atexit

class VALISSystemLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.valis_dir = Path(__file__).parent
        
        # Register cleanup on exit
        atexit.register(self.cleanup_processes)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nShutting down VALIS system...")
        self.cleanup_processes()
        sys.exit(0)
    
    def cleanup_processes(self):
        """Clean up backend and frontend processes"""
        if self.backend_process:
            print("Stopping VALIS API backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("Stopping React frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
    
    def check_node_npm(self):
        """Check if Node.js and npm are available"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_frontend_dependencies(self):
        """Install npm dependencies if needed"""
        frontend_dir = self.valis_dir / 'frontend'
        node_modules = frontend_dir / 'node_modules'
        
        if not node_modules.exists():
            print("Installing frontend dependencies...")
            try:
                subprocess.run(
                    ['npm', 'install'],
                    cwd=frontend_dir,
                    check=True,
                    timeout=300
                )
                print("✅ Frontend dependencies installed")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"❌ Failed to install dependencies: {e}")
                return False
        else:
            print("✅ Frontend dependencies already installed")
            return True
    
    def start_backend(self):
        """Start the VALIS API backend"""
        print("Starting VALIS Enhanced API Backend...")
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, 'start_enhanced_api_server.py'],
                cwd=self.valis_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ VALIS API Backend started on http://localhost:8000")
                return True
            else:
                print("❌ Backend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend"""
        print("Starting VALIS React Frontend...")
        
        frontend_dir = self.valis_dir / 'frontend'
        
        try:
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait for frontend to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ React Frontend started on http://localhost:3000")
                return True
            else:
                print("❌ Frontend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def open_browser(self):
        """Open the VALIS interface in the default browser"""
        print("Opening VALIS interface in browser...")
        try:
            webbrowser.open('http://localhost:3000')
            print("✅ Browser opened to http://localhost:3000")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
    
    def launch_system(self):
        """Launch the complete VALIS system"""
        print("VALIS COMPLETE SYSTEM LAUNCHER")
        print("=" * 60)
        print("Temporal-Safe AI Democratization Platform")
        print("Doc Brown's Full Implementation")
        print("Enhanced API + React Dashboard Integration")
        print("-" * 60)
        
        # Check prerequisites
        print("1. Checking prerequisites...")
        if not self.check_node_npm():
            print("[ERROR] Node.js and npm are required for the frontend")
            print("   Please install Node.js from https://nodejs.org/")
            return False
        print("[OK] Node.js and npm available")
        
        # Install frontend dependencies
        print("\n2. Preparing frontend...")
        if not self.install_frontend_dependencies():
            return False
        
        # Start backend
        print("\n3. Starting VALIS API Backend...")
        if not self.start_backend():
            return False
        
        # Start frontend
        print("\n4. Starting React Frontend...")
        if not self.start_frontend():
            return False
        
        # Open browser
        print("\n5. Opening browser interface...")
        time.sleep(2)  # Give frontend a moment to fully start
        self.open_browser()
        
        print("\n🎭 VALIS DEMOCRATIZATION PLATFORM LAUNCHED!")
        print("=" * 60)
        print("API Backend: http://localhost:8000")
        print("React Frontend: http://localhost:3000")
        print("API Documentation: http://localhost:8000/docs")
        print("-" * 60)
        print("All temporal safeguards active")
        print("Real-time AI persona chat available")
        print("System diagnostics monitoring")
        print("Message history with auto-cleanup")
        print("-" * 60)
        print("Press Ctrl+C to stop the system")
        print()
        
        return True
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        try:
            while True:
                time.sleep(5)
                
                # Check backend
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died, restarting...")
                    self.start_backend()
                
                # Check frontend
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died, restarting...")
                    self.start_frontend()
                    
        except KeyboardInterrupt:
            pass

def main():
    launcher = VALISSystemLauncher()
    
    if launcher.launch_system():
        try:
            launcher.monitor_processes()
        except KeyboardInterrupt:
            pass
    
    launcher.cleanup_processes()
    print("\n🎯 VALIS system shutdown complete")

if __name__ == "__main__":
    main()
