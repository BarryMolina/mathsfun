#!/usr/bin/env python3
from ui import (
    print_welcome,
    print_main_menu,
    print_authentication_menu,
    print_authentication_status,
)
from addition import addition_mode
from addition_tables import addition_tables_mode
from auth import authenticate_user, validate_environment


def authentication_flow():
    """Handle user authentication"""
    valid, message = validate_environment()
    if not valid:
        print_authentication_status(message, False)
        return False

    while True:
        print_authentication_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            return False
        elif choice == "1":
            print_authentication_status("Opening browser for Google authentication...")
            print("Please complete the authentication in your browser.")
            print("This window will close automatically after authentication.")

            result = authenticate_user()

            if result and result.get("success"):
                print_authentication_status(
                    "Authentication successful! Welcome to MathsFun!"
                )
                print(result)
                return True
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

    if not authentication_flow():
        print("\n👋 Thanks for visiting MathsFun!")
        return

    while True:
        print_main_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            print("\n👋 Thanks for using MathsFun! Keep practicing!")
            break
        elif choice == "1":
            addition_mode()
        elif choice == "2":
            addition_tables_mode()
        else:
            print("❌ Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
