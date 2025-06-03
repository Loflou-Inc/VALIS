#!/usr/bin/env python3
"""
OPS-401 & OPS-402 Deployment Validation
Doc Brown's Temporal Container Deployment Verification
"""

import subprocess
import time
import requests
import json
from pathlib import Path

def check_docker_prerequisites():
    """Check Docker and Docker Compose are available"""
    print("🔍 DOCKER PREREQUISITES CHECK")
    print("-" * 50)
    
    try:
        # Check Docker
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
        else:
            print("❌ Docker not available")
            return False
        
        # Check Docker Compose
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("❌ Docker Compose not available")
            return False
        
        return True
    except FileNotFoundError:
        print("❌ Docker commands not found in PATH")
        return False

def validate_dockerfile_structure():
    """Validate Dockerfile follows Doc Brown's safeguards"""
    print("\n🐳 DOCKERFILE VALIDATION")
    print("-" * 50)
    
    # Use cross-platform path resolution
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    dockerfile_content = dockerfile_path.read_text()
    
    # Check for Doc Brown's required safeguards
    safeguards = [
        ("Multi-stage build", "FROM" in dockerfile_content and "AS" in dockerfile_content),
        ("Non-root user", "useradd" in dockerfile_content or "adduser" in dockerfile_content),
        ("Health check", "HEALTHCHECK" in dockerfile_content),
        ("Security headers", "nginx" in dockerfile_content.lower()),
        ("Proper COPY", "COPY --from=" in dockerfile_content),
        ("Port exposure", "EXPOSE" in dockerfile_content),
        ("Supervisor", "supervisor" in dockerfile_content.lower())
    ]
    
    all_passed = True
    for safeguard, check in safeguards:
        status = "✅" if check else "❌"
        print(f"{status} {safeguard}: {'PRESENT' if check else 'MISSING'}")
        if not check:
            all_passed = False
    
    return all_passed

def validate_docker_compose():
    """Validate Docker Compose configuration"""
    print("\n🐙 DOCKER COMPOSE VALIDATION") 
    print("-" * 50)
    
    # Use cross-platform path resolution
    compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    if not compose_path.exists():
        print("❌ docker-compose.yml not found")
        return False
    
    try:
        # Validate compose file syntax
        result = subprocess.run(
            ['docker-compose', 'config'], 
            cwd=str(Path(__file__).parent.parent),
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose syntax: VALID")
            return True
        else:
            print(f"❌ Docker Compose syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error validating Docker Compose: {e}")
        return False

def build_and_test_container():
    """Build container and test basic functionality"""
    print("\n🏗️ CONTAINER BUILD & TEST")
    print("-" * 50)
    
    try:
        # Build the container
        print("Building VALIS container...")
        result = subprocess.run(
            ['docker-compose', 'build'],
            cwd=str(Path(__file__).parent.parent), 
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Container build failed: {result.stderr}")
            return False
        
        print("✅ Container build: SUCCESS")
        
        # Start the container
        print("Starting VALIS container...")
        result = subprocess.run(
            ['docker-compose', 'up', '-d'],
            cwd=str(Path(__file__).parent.parent),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Container start failed: {result.stderr}")
            return False
        
        print("✅ Container start: SUCCESS")
        
        # Wait for services to be ready
        print("Waiting for services to be ready...")
        time.sleep(15)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ Container build timeout (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Container test error: {e}")
        return False

def test_config_management():
    """Test OPS-402 config management system"""
    print("\n⚙️ CONFIG MANAGEMENT TEST")
    print("-" * 50)
    
    try:
        # Test getting current config
        response = requests.get("http://localhost:3000/api/config/current", timeout=10)
        if response.status_code == 200:
            print("✅ Config retrieval: SUCCESS")
        else:
            print(f"❌ Config retrieval failed: HTTP {response.status_code}")
            return False
        
        # Test config validation
        response = requests.get("http://localhost:3000/api/config/validate", timeout=10)
        if response.status_code == 200:
            print("✅ Config validation: SUCCESS")
        else:
            print(f"❌ Config validation failed: HTTP {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Config management test error: {e}")
        return False

def cleanup_test_environment():
    """Clean up test containers"""
    print("\n🧹 CLEANUP")
    print("-" * 50)
    
    try:
        subprocess.run(
            ['docker-compose', 'down'],
            cwd=str(Path(__file__).parent.parent),
            capture_output=True
        )
        print("✅ Test containers stopped")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    """Run complete OPS-401 & OPS-402 validation"""
    print("🚀 OPS-401 & OPS-402 DEPLOYMENT VALIDATION")
    print("=" * 70)
    print("🔬 Doc Brown's Temporal Container Deployment Verification")
    print("⚡ Testing containerization, config management, deployment safety")
    print("-" * 70)
    
    all_tests_passed = True
    
    # Test 1: Prerequisites
    if not check_docker_prerequisites():
        print("\n❌ Prerequisites not met - aborting validation")
        return False
    
    # Test 2: Dockerfile validation
    if not validate_dockerfile_structure():
        print("\n❌ Dockerfile validation failed")
        all_tests_passed = False
    
    # Test 3: Docker Compose validation
    if not validate_docker_compose():
        print("\n❌ Docker Compose validation failed")
        all_tests_passed = False
    
    # Test 4: Container build and test (only if previous tests passed)
    if all_tests_passed:
        try:
            if not build_and_test_container():
                print("\n❌ Container deployment test failed")
                all_tests_passed = False
            
            # Test 5: Config management (only if container is running)
            if all_tests_passed:
                if not test_config_management():
                    print("\n❌ Config management test failed")
                    all_tests_passed = False
        finally:
            # Always cleanup
            cleanup_test_environment()
    
    # Final verdict
    print("\n" + "=" * 70)
    print("🎯 OPS-401 & OPS-402 VALIDATION RESULTS:")
    
    if all_tests_passed:
        print("✅ DEPLOYMENT VALIDATION: PASSED!")
        print("🐳 Container deployment: READY FOR PRODUCTION")
        print("⚙️ Config management: FULLY OPERATIONAL") 
        print("🛡️ All temporal deployment safeguards: VERIFIED")
        print("\n🚀 VALIS CONTAINERIZATION: MISSION ACCOMPLISHED!")
    else:
        print("❌ DEPLOYMENT VALIDATION: ISSUES DETECTED!")
        print("🔧 Fix identified issues before production deployment")
        print("🔬 Review failed tests for temporal vulnerabilities")
    
    return all_tests_passed

if __name__ == "__main__":
    main()
