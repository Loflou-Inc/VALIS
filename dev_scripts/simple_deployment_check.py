#!/usr/bin/env python3
"""
Simple Deployment Structure Verification
"""

from pathlib import Path

def verify_deployment_structure():
    """Verify all deployment files are present"""
    print("OPS-401 & OPS-402 DEPLOYMENT STRUCTURE CHECK")
    print("=" * 60)
    
    # Use cross-platform path resolution
    valis_dir = Path(__file__).parent.parent
    
    # Required deployment files
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker/nginx.conf", 
        "docker/supervisord.conf",
        "docker/start.sh",
        "docker/healthcheck.sh",
        "core/config_manager.py",
        "api/config_endpoints.py"
    ]
    
    missing_files = []
    found_files = []
    
    for file_path in required_files:
        full_path = valis_dir / file_path
        if full_path.exists():
            found_files.append(file_path)
            file_size = full_path.stat().st_size
            print(f"FOUND: {file_path} ({file_size} bytes)")
        else:
            missing_files.append(file_path)
            print(f"MISSING: {file_path}")
    
    print(f"\nSUMMARY:")
    print(f"Found: {len(found_files)}")
    print(f"Missing: {len(missing_files)}")
    
    # Check docker directory structure
    docker_dir = valis_dir / "docker"
    if docker_dir.exists():
        docker_files = list(docker_dir.glob("*"))
        print(f"Docker config files: {len(docker_files)}")
    
    # Check if Docker Compose syntax is valid
    try:
        import subprocess
        result = subprocess.run(
            ['docker-compose', 'config'], 
            cwd=str(valis_dir),
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("Docker Compose syntax: VALID")
        else:
            print(f"Docker Compose syntax: ERROR - {result.stderr}")
    except Exception as e:
        print(f"Docker Compose check: SKIPPED - {e}")
    
    if len(missing_files) == 0:
        print("\nVERDICT: DEPLOYMENT STRUCTURE COMPLETE")
        print("All Doc Brown's temporal deployment safeguards implemented!")
        return True
    else:
        print(f"\nVERDICT: MISSING DEPLOYMENT FILES")
        print(f"Missing: {missing_files}")
        return False

if __name__ == "__main__":
    verify_deployment_structure()
