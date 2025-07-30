#!/usr/bin/env python3
"""
Simple test to verify that the environment detection fix works
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.database.supabase_manager import create_supabase_manager

def test_environment_detection():
    """Test that use_local parameter correctly configures environments"""
    
    # Test production configuration (default)
    print("Testing production configuration...")
    prod_manager = create_supabase_manager(use_local=False)
    print(f"  Environment: {prod_manager.config.environment}")
    print(f"  Is Local: {prod_manager.config.is_local}")
    print(f"  URL: {prod_manager.config.url}")
    print()
    
    # Test local configuration  
    print("Testing local configuration...")
    local_manager = create_supabase_manager(use_local=True)
    print(f"  Environment: {local_manager.config.environment}")
    print(f"  Is Local: {local_manager.config.is_local}")
    print(f"  URL: {local_manager.config.url}")
    print()
    
    # Verify they're different
    assert prod_manager.config.environment != local_manager.config.environment
    assert prod_manager.config.is_local != local_manager.config.is_local
    
    print("✅ Environment detection is working correctly!")
    print(f"Production: {prod_manager.config.environment} (is_local={prod_manager.config.is_local})")
    print(f"Local: {local_manager.config.environment} (is_local={local_manager.config.is_local})")

if __name__ == "__main__":
    test_environment_detection()