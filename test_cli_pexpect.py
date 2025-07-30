#!/usr/bin/env python3
"""
Test script using pexpect to interact with the CLI application
"""
import pexpect
import sys
import time

def test_cli_local_environment():
    """Test CLI with --local flag using pexpect"""
    print("Starting CLI test with --local flag...")
    
    try:
        # Start the CLI application with --local flag
        child = pexpect.spawn('python3 main.py --local', encoding='utf-8')
        child.logfile = sys.stdout  # Show output in real-time
        
        # Wait for the environment detection message
        index = child.expect([
            '🌐 Using production Supabase environment',
            '🔧 Using local Supabase environment',
            pexpect.TIMEOUT,
            pexpect.EOF
        ], timeout=10)
        
        if index == 0:
            print("\n❌ ISSUE FOUND: Application is using production environment despite --local flag")
            environment_used = "production"
        elif index == 1:
            print("\n✅ SUCCESS: Application is using local environment as expected")
            environment_used = "local"
        elif index == 2:
            print("\n⏰ TIMEOUT: No environment message detected within 10 seconds")
            environment_used = "timeout"
        else:
            print("\n❌ EOF: Process ended unexpectedly")
            environment_used = "eof"
        
        # Wait for menu to appear
        try:
            child.expect('Select an option:', timeout=5)
            print("\n✅ Main menu appeared successfully")
            
            # Send 'exit' to close the application
            child.sendline('exit')
            child.expect(pexpect.EOF, timeout=5)
            print("✅ Application exited cleanly")
            
        except pexpect.TIMEOUT:
            print("\n⏰ Menu did not appear within expected time")
            child.terminate()
        except pexpect.EOF:
            print("\n❌ Application ended before showing menu")
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return "error"
    
    return environment_used

def test_cli_without_flag():
    """Test CLI without --local flag for comparison"""
    print("\n" + "="*50)
    print("Starting CLI test WITHOUT --local flag for comparison...")
    
    try:
        # Start the CLI application without --local flag
        child = pexpect.spawn('python3 main.py', encoding='utf-8')
        child.logfile = sys.stdout  # Show output in real-time
        
        # Wait for the environment detection message
        index = child.expect([
            '🌐 Using production Supabase environment',
            '🔧 Using local Supabase environment',
            pexpect.TIMEOUT,
            pexpect.EOF
        ], timeout=10)
        
        if index == 0:
            print("\n✅ Expected: Application is using production environment without --local flag")
            environment_used = "production"
        elif index == 1:
            print("\n❓ Unexpected: Application is using local environment without --local flag")
            environment_used = "local"
        elif index == 2:
            print("\n⏰ TIMEOUT: No environment message detected within 10 seconds")
            environment_used = "timeout"
        else:
            print("\n❌ EOF: Process ended unexpectedly")
            environment_used = "eof"
        
        # Wait for menu to appear
        try:
            child.expect('Select an option:', timeout=5)
            print("✅ Main menu appeared successfully")
            
            # Send 'exit' to close the application
            child.sendline('exit')
            child.expect(pexpect.EOF, timeout=5)
            print("✅ Application exited cleanly")
            
        except pexpect.TIMEOUT:
            print("⏰ Menu did not appear within expected time")
            child.terminate()
        except pexpect.EOF:
            print("❌ Application ended before showing menu")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return "error"
    
    return environment_used

if __name__ == "__main__":
    print("🧪 Testing MathsFun CLI Environment Detection")
    print("=" * 50)
    
    # Test with --local flag
    local_result = test_cli_local_environment()
    
    # Test without --local flag for comparison
    normal_result = test_cli_without_flag()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"With --local flag: {local_result}")
    print(f"Without --local flag: {normal_result}")
    
    if local_result == "production" and normal_result == "production":
        print("\n❌ ISSUE CONFIRMED: --local flag is not working correctly")
        print("Both tests show production environment")
    elif local_result == "local" and normal_result == "production":
        print("\n✅ WORKING CORRECTLY: --local flag successfully switches to local environment")
    else:
        print(f"\n❓ UNEXPECTED RESULT: local={local_result}, normal={normal_result}")