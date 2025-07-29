#!/usr/bin/env python3
import re
import getpass
from typing import Optional


def print_welcome():
    """Display a fun welcome message for MathsFun"""
    print("\n" + "=" * 50)
    print("🎯 Welcome to MathsFun! 🎯")
    print("Let's make math practice fun and interactive!")
    print("=" * 50 + "\n")


def print_main_menu():
    """Display the main menu options"""
    print("📚 Main Menu:")
    print("1. Addition")
    print("2. Addition Tables")
    print("3. Sign out")
    print("\nType 'exit' to quit the application")
    print("-" * 30)


def print_authentication_menu():
    """Display authentication options and status"""
    print("🔐 Authentication Required")
    print("Please sign in to access MathsFun")
    print("1. Sign in with Google")
    print("2. Sign in with email/password")
    print("3. Sign up with email/password")
    print("Type 'exit' to quit the application")
    print("-" * 30)


def print_authentication_status(message: str, success: bool = True):
    """Display authentication status messages"""
    emoji = "✅" if success else "❌"
    print(f"\n{emoji} {message}\n")


def print_user_welcome(user_data: dict):
    """Display personalized welcome message with user data"""
    name = user_data.get("name", "User")
    email = user_data.get("email", "")

    print(f"\n🎉 Welcome back, {name}!")
    print(f"📧 Signed in as: {email}")
    if user_data.get("avatar_url"):
        print(f"🖼️  Profile picture: {user_data['avatar_url']}")
    print("-" * 50)


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def get_email_input() -> str:
    """Get and validate email input from user"""
    while True:
        email = input("Email: ").strip()

        if not email:
            print("❌ Email cannot be empty. Please try again.")
            continue

        # Basic email validation using regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            print("❌ Please enter a valid email address (e.g., user@example.com)")
            continue

        return email


def get_password_input(prompt: str = "Password") -> str:
    """Get secure password input from user (input is hidden)"""
    import os
    
    while True:
        # Use regular input for automation testing to avoid getpass/pexpect issues
        if os.getenv('MATHSFUN_TEST_MODE'):
            password = input(f"{prompt}: ")
        else:
            password = getpass.getpass(f"{prompt}: ")

        if not password:
            print("❌ Password cannot be empty. Please try again.")
            continue

        if len(password) < 6:
            print("❌ Password must be at least 6 characters long. Please try again.")
            continue

        return password


def get_password_confirmation() -> str:
    """Get password confirmation for signup"""
    import os
    
    password = get_password_input("Create password")

    while True:
        # Use regular input for automation testing to avoid getpass/pexpect issues
        if os.getenv('MATHSFUN_TEST_MODE'):
            confirmation = input("Confirm password: ")
        else:
            confirmation = getpass.getpass("Confirm password: ")

        if password == confirmation:
            return password

        print("❌ Passwords do not match. Please try again.")
        password = get_password_input("Create password")
