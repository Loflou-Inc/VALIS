#!/usr/bin/env python3
"""
Simple VALIS Frontend Verification Script
"""

import os
import sys
from pathlib import Path

def check_frontend_files():
    """Check if all required frontend files exist"""
    frontend_dir = Path('C:/VALIS/frontend')
    
    print("VALIS Frontend Structure Check")
    print("=" * 40)
    
    if not frontend_dir.exists():
        print("ERROR: Frontend directory not found!")
        return False
    
    required_files = [
        'package.json',
        'vite.config.ts', 
        'tsconfig.json',
        'tailwind.config.js',
        'src/App.tsx',
        'src/main.tsx',
        'src/components/MainLayout.tsx',
        'src/components/Header.tsx',
        'src/components/Sidebar.tsx', 
        'src/components/ChatInterface.tsx',
        'src/components/SystemDiagnostics.tsx',
        'src/components/ui/button.tsx',
        'src/components/ui/card.tsx',
        'src/components/ui/badge.tsx',
        'src/components/ui/input.tsx',
        'src/lib/api.ts',
        'src/types/index.ts',
        'index.html'
    ]
    
    missing_files = []
    existing_files = []
    
    for file in required_files:
        file_path = frontend_dir / file
        if file_path.exists():
            existing_files.append(file)
            print(f"FOUND: {file}")
        else:
            missing_files.append(file)
            print(f"MISSING: {file}")
    
    print(f"\nSUMMARY:")
    print(f"Found: {len(existing_files)} files")
    print(f"Missing: {len(missing_files)} files")
    
    if missing_files:
        print(f"\nMissing files: {missing_files}")
        return False
    else:
        print(f"\nFrontend structure: COMPLETE")
        return True

if __name__ == "__main__":
    check_frontend_files()
