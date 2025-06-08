#!/usr/bin/env python3
"""
Local Test Runner for VALIS Sprint 1.1
Runs the test suite locally to verify setup before CI
"""
import subprocess
import sys
import os
from pathlib import Path

# Add VALIS to path
sys.path.append(str(Path(__file__).parent.parent))

def run_tests():
    """Run the VALIS test suite locally"""
    
    print("=" * 60)
    print("VALIS Sprint 1.1: Test Infrastructure Verification")
    print("=" * 60)
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✓ pytest version: {pytest.__version__}")
    except ImportError:
        print("✗ pytest not installed. Run: pip install -r requirements.txt")
        return False
    
    # Check if coverage is available
    try:
        import coverage
        print(f"✓ coverage version: {coverage.__version__}")
    except ImportError:
        print("! coverage not available - install pytest-cov for coverage reports")
    
    print("\n" + "-" * 60)
    print("Running VALIS Test Suite...")
    print("-" * 60)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--cov=agents",
        "--cov=memory", 
        "--cov=core",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=25",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED - Sprint 1.1 Test Infrastructure Complete!")
            print("=" * 60)
            print("Coverage report generated in: htmlcov/index.html")
            print("Test infrastructure is ready for development.")
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ Some tests failed - check output above")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
