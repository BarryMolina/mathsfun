#!/usr/bin/env python3
"""Test runner script for MathsFun application."""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        print("Make sure pytest is installed: pip install -r requirements.txt")
        return False


def main():
    """Run the test suite with various configurations."""
    print("🎯 MathsFun Test Suite Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('tests'):
        print("❌ Tests directory not found. Please run from the project root.")
        sys.exit(1)
    
    # Check if pytest is available
    try:
        subprocess.run(['pytest', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest not found. Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Run different test configurations
    test_configs = [
        (['pytest', 'tests/', '-v'], "Running All Tests (Verbose)"),
        (['pytest', 'tests/', '--cov=.', '--cov-report=term-missing'], "Running Tests with Coverage"),
        (['pytest', 'tests/', '-m', 'not slow'], "Running Fast Tests Only"),
        (['pytest', 'tests/test_ui.py', '-v'], "Running UI Tests"),
        (['pytest', 'tests/test_addition.py', '-v'], "Running Addition Logic Tests"),
        (['pytest', 'tests/test_session.py', '-v'], "Running Session Tests"),
        (['pytest', 'tests/test_integration.py', '-v'], "Running Integration Tests"),
    ]
    
    results = []
    for command, description in test_configs:
        success = run_command(command, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print('='*60)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {description}")
    
    # Overall result
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 All test suites passed!")
        sys.exit(0)
    else:
        print("\n💥 Some test suites failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()