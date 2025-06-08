#!/usr/bin/env python3
"""
VALIS Environment Setup Script - Sprint 1.3
Generates secure environment configuration for VALIS deployment
"""
import os
import secrets
import shutil
import sys
from pathlib import Path

def generate_secure_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(length)

def setup_environment():
    """
    Set up VALIS environment configuration
    
    Steps:
    1. Copy .env.template to .env (if it doesn't exist)
    2. Generate secure random values for secrets
    3. Replace placeholders with generated values
    4. Display setup instructions
    """
    print("[+] VALIS Environment Setup - Sprint 1.3")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("[!] .env file already exists!")
        response = input("Do you want to regenerate secrets? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled. Existing .env file preserved.")
            return False
        
        # Backup existing .env
        backup_name = f".env.backup.{secrets.token_hex(4)}"
        shutil.copy('.env', backup_name)
        print(f"[+] Backed up existing .env to {backup_name}")
    
    # Check if template exists
    if not os.path.exists('.env.template'):
        print("[-] Error: .env.template file not found!")
        print("Please ensure you're running this from the VALIS root directory.")
        return False
    
    print("[+] Copying .env.template to .env...")
    shutil.copy('.env.template', '.env')
    
    # Generate secure secrets
    print("[+] Generating secure secrets...")
    secrets_generated = {
        'database_password': generate_secure_key(16),
        'secret_key': generate_secure_key(32),
        'admin_api_key': generate_secure_key(24),
        'jwt_secret': generate_secure_key(32)
    }
    # Read .env content
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace placeholders with generated values
    replacements = {
        'your_secure_database_password_here': secrets_generated['database_password'],
        'your_32_character_secret_key_here': secrets_generated['secret_key'],
        'your_admin_api_key_here': secrets_generated['admin_api_key'],
        'your_jwt_secret_key_here': secrets_generated['jwt_secret']
    }
    
    print("[+] Replacing placeholders with secure values...")
    for placeholder, secure_value in replacements.items():
        content = content.replace(placeholder, secure_value)
        print(f"   [+] Replaced {placeholder[:20]}...")
    
    # Write updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n[+] Environment setup complete!")
    print("\n[!] Generated secure secrets:")
    print(f"   Database Password: {secrets_generated['database_password']}")
    print(f"   Secret Key: {secrets_generated['secret_key'][:16]}...")
    print(f"   Admin API Key: {secrets_generated['admin_api_key'][:16]}...")
    print(f"   JWT Secret: {secrets_generated['jwt_secret'][:16]}...")
    
    print("\n[>] Next steps:")
    print("   1. Edit .env and add your API keys (OpenAI, Anthropic)")
    print("   2. Update database connection settings if needed")
    print("   3. Test configuration: python -c 'from core.config import get_config; get_config()'")
    print("   4. NEVER commit .env to version control!")
    
    return True

def validate_setup():
    """Validate that the setup was successful"""
    try:
        from core.config import get_config
        config = get_config()
        print("[+] Configuration validation successful!")
        print(f"   Environment: {config.environment}")
        print(f"   Database: {config.db_host}:{config.db_port}/{config.db_name}")
        return True
    except Exception as e:
        print(f"[-] Configuration validation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Starting VALIS environment setup...")
    
    try:
        if setup_environment():
            print("\n[>] Testing configuration...")
            if validate_setup():
                print("\n[+] VALIS environment setup complete and validated!")
                print("Your system is ready for secure deployment.")
            else:
                print("\n[!] Setup completed but validation failed.")
                print("Please check your configuration manually.")
        else:
            print("\n[-] Environment setup failed.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n[-] Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()