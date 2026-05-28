#!/usr/bin/env python3
"""
Bootstrap authentication by leveraging gcloud's existing session
This creates a workaround for Application Default Credentials
"""

import subprocess
import json
import os
from pathlib import Path
import sys

def get_gcloud_token():
    """Try to get token from gcloud"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"Cannot get token from gcloud: {e}")
    
    return None

def create_credentials_wrapper():
    """
    Create a wrapper that uses gcloud's cached tokens
    """
    wrapper_code = '''
import subprocess
import json
from pathlib import Path

class GCloudCredentials:
    """Credentials wrapper that uses gcloud's cached tokens"""
    
    def __init__(self):
        self.token = None
        self.refresh()
    
    def refresh(self, request=None):
        """Get fresh token from gcloud"""
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            self.token = result.stdout.strip()
        else:
            raise RuntimeError(f"Failed to get gcloud token: {result.stderr}")
    
    @property
    def valid(self):
        return self.token is not None
    
    @property
    def expired(self):
        return False

# Export for use
credentials = GCloudCredentials()
'''
    
    wrapper_path = Path.home() / ".config" / "gcloud" / "gcloud_creds_wrapper.py"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_code)
    
    return wrapper_path

def main():
    print("🔧 Bootstrap Google Sheets API Authentication")
    print("=" * 50)
    print("")
    
    # Check if we can get token
    print("Checking gcloud authentication...")
    token = get_gcloud_token()
    
    if token:
        print(f"✅ Got gcloud token: {token[:20]}...")
        
        # Create a wrapper module
        wrapper_path = create_credentials_wrapper()
        print(f"✅ Created credentials wrapper at {wrapper_path}")
        
        # Update skills to use this wrapper
        print("\n📝 Next steps:")
        print("1. Run: python3 run_pipeline.py")
        print("   This will use gcloud's cached tokens")
        print("")
        print("2. If that fails, you need to authenticate on your local machine:")
        print("   $ bash setup_google_auth.sh")
        
        return 0
    
    else:
        print("❌ Cannot get token from gcloud")
        print("\n📝 To fix this:")
        print("1. On your LOCAL MACHINE (with browser), run:")
        print("   $ gcloud auth login")
        print("   $ gcloud auth application-default login")
        print("")
        print("2. Then run the pipeline again:")
        print("   $ python3 run_pipeline.py")
        
        return 1

if __name__ == "__main__":
    exit(main())
