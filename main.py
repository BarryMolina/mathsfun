#!/usr/bin/env python3
from ui import (
    print_welcome,
    print_main_menu,
    print_authentication_menu,
    print_authentication_status,
    print_user_welcome,
)
from addition import addition_mode
from addition_tables import addition_tables_mode
from supabase_client import supabase, validate_environment


def authentication_flow():
    """Handle user authentication"""
    valid, message = validate_environment()
    if not valid:
        print_authentication_status(message, False)
        return False, None

    while True:
        print_authentication_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            return False, None
        elif choice == "1":
            result = supabase.sign_in_with_google()

            if result and result.get("success"):
                user_data = result.get("user")
                session_data = result.get("session")

                print_authentication_status("Authentication successful!")
                if user_data:
                    print_user_welcome(user_data)

                return True, {"user": user_data, "session": session_data}
            else:
                error_msg = (
                    result.get("error", "Unknown error")
                    if result
                    else "Authentication failed"
                )
                print_authentication_status(
                    f"Authentication failed: {error_msg}", False
                )
        else:
            print("❌ Invalid option. Please try again.\n")


def main():
    """Main application loop"""
    print_welcome()

    auth_success, auth_data = authentication_flow()
    if not auth_success:
        print("\n👋 Thanks for visiting MathsFun!")
        return

    # Store user and session data for use throughout the application
    user_data = auth_data.get("user") if auth_data else None

    while True:
        print_main_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            name = user_data.get("name", "User") if user_data else "User"
            print(f"\n👋 Thanks for using MathsFun, {name}! Keep practicing!")
            break
        elif choice == "1":
            addition_mode()
        elif choice == "2":
            addition_tables_mode()
        else:
            print("❌ Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
