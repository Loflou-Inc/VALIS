#!/usr/bin/env python3
"""
VALIS Frontend Verification Script
Test React Dashboard Integration with VALIS API
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_backend_health():
    """Check if VALIS API backend is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ VALIS API Backend: {health_data.get('status', 'unknown')}")
            print(f"   Providers: {len(health_data.get('providers_available', []))}")
            print(f"   Active Sessions: {health_data.get('active_sessions', 0)}")
            return True
        else:
            print(f"❌ VALIS API Backend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VALIS API Backend: {e}")
        return False

def verify_frontend_setup():
    """Verify frontend project structure and dependencies"""
    frontend_dir = Path('C:/VALIS/frontend')
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    required_files = [
        'package.json',
        'vite.config.ts',
        'tsconfig.json',
        'tailwind.config.js',
        'src/App.tsx',
        'src/main.tsx',
        'index.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not (frontend_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Frontend project structure complete")
    return True

def install_dependencies():
    """Install npm dependencies"""
    frontend_dir = Path('C:/VALIS/frontend')
    
    print("📦 Installing frontend dependencies...")
    try:
        result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ npm install failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ npm install timed out")
        return False
    except Exception as e:
        print(f"❌ npm install error: {e}")
        return False

def main():
    print("🚀 VALIS FRONTEND VERIFICATION")
    print("=" * 50)
    print("Doc Brown's UI-201, UI-202, UI-203 Implementation Test")
    print()
    
    # Check backend
    print("1. Checking VALIS API Backend...")
    backend_ok = check_backend_health()
    print()
    
    # Verify frontend setup
    print("2. Verifying frontend project structure...")
    frontend_ok = verify_frontend_setup()
    print()
    
    # Install dependencies
    if frontend_ok:
        print("3. Installing dependencies...")
        deps_ok = install_dependencies()
        print()
    else:
        deps_ok = False
    
    # Summary
    print("VERIFICATION SUMMARY:")
    print("=" * 30)
    print(f"Backend API: {'✅' if backend_ok else '❌'}")
    print(f"Frontend Structure: {'✅' if frontend_ok else '❌'}")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print()
    
    if backend_ok and frontend_ok and deps_ok:
        print("🎯 VALIS FRONTEND READY FOR LAUNCH!")
        print()
        print("To start the development server:")
        print("1. cd C:\\VALIS\\frontend")
        print("2. npm run dev")
        print("3. Open http://localhost:3000")
        print()
        print("The frontend will connect to the VALIS API at http://localhost:8000")
    else:
        print("❌ VALIS Frontend setup incomplete")
        if not backend_ok:
            print("   - Start VALIS API backend first: python start_enhanced_api_server.py")
        if not frontend_ok:
            print("   - Frontend project structure issues detected")
        if not deps_ok:
            print("   - npm dependencies installation failed")

if __name__ == "__main__":
    main()
