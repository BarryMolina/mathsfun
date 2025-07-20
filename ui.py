#!/usr/bin/env python3
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
    print("\nType 'exit' to quit the application")
    print("-" * 30)


def print_authentication_menu():
    """Display authentication options and status"""
    print("🔐 Authentication Required")
    print("Please sign in to access MathsFun")
    print("1. Sign in with Google")
    print("Type 'exit' to quit the application")
    print("-" * 30)


def print_authentication_status(message: str, success: bool = True):
    """Display authentication status messages"""
    emoji = "✅" if success else "❌"
    print(f"\n{emoji} {message}\n")


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()