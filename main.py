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
from supabase_client import supabase_client, validate_environment


def get_current_user():
    """Get current user data from Supabase client"""
    try:
        if not supabase_client.is_authenticated():
            return None
            
        client = supabase_client.get_client()
        response = client.auth.get_user()
        
        if response and response.user:
            user = response.user
            
            # Extract user data in consistent format
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": (
                    user.user_metadata.get("full_name") if user.user_metadata
                    else user.user_metadata.get("name", "Unknown") if user.user_metadata
                    else "Unknown"
                ),
                "avatar_url": user.user_metadata.get("avatar_url") if user.user_metadata else None,
                "provider": (
                    user.app_metadata.get("provider", "google") if user.app_metadata
                    else "google"
                ),
                "last_sign_in": user.last_sign_in_at,
            }
            return user_data
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None


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
            result = supabase_client.sign_in_with_google()

            if result and result.get("success"):
                print_authentication_status("Authentication successful!")
                
                # Fetch fresh user data from Supabase client
                user_data = get_current_user()
                if user_data:
                    print_user_welcome(user_data)

                return True, user_data
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

    auth_success, user_data = authentication_flow()
    if not auth_success:
        print("\n👋 Thanks for visiting MathsFun!")
        return

    # Refresh user data from Supabase client for main loop
    if not user_data:
        user_data = get_current_user()
        if not user_data:
            print("❌ Unable to fetch user data. Please try again.")
            return

    while True:
        # Check if still authenticated before showing menu
        if not supabase_client.is_authenticated():
            print("❌ Authentication session expired. Please sign in again.")
            break
            
        print_main_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            # Get fresh user data for goodbye message
            current_user = get_current_user()
            name = current_user.get("name", "User") if current_user else "User"
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
