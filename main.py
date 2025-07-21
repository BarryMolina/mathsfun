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
from container import Container




def authentication_flow(container):
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
                
                # Fetch fresh user data from UserService
                user = container.user_svc.get_current_user(supabase_client)
                if user:
                    # Convert User model to dict for UI compatibility
                    user_data = {
                        "name": user.display_name,
                        "email": user.email,
                        "avatar_url": None  # Not available from auth data
                    }
                    print_user_welcome(user_data)

                return True, user
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

    while True:  # Outer loop for authentication flow
        # Initialize the container with Supabase client early
        container = Container(supabase_client.get_client())
        
        # Try to restore from saved session first
        auto_login_success = False
        user = None
        
        if supabase_client.load_persisted_session():
            user = container.user_svc.get_current_user(supabase_client)
            if user:
                print(f"✅ Welcome back, {user.display_name or 'User'}!")
                print("🔄 Restored previous session\n")
                auto_login_success = True
            else:
                print("⚠️  Stored session invalid, please sign in again")
        
        # If auto-login failed, go through normal authentication flow
        if not auto_login_success:
            auth_success, user = authentication_flow(container)
            if not auth_success:
                print("\n👋 Thanks for visiting MathsFun!")
                return

        # Refresh user data from UserService for main loop
        if not user:
            user = container.user_svc.get_current_user(supabase_client)
            if not user:
                print("❌ Unable to fetch user data. Please try again.")
                continue  # Return to authentication

        # Inner loop for main menu
        while True:
            # Check if still authenticated before showing menu
            if not supabase_client.is_authenticated():
                print("❌ Authentication session expired. Please sign in again.")
                break  # Return to authentication flow
                
            print_main_menu()
            choice = input("Select an option: ").strip().lower()

            if choice == "exit":
                # Get fresh user data for goodbye message
                current_user = container.user_svc.get_current_user(supabase_client)
                name = current_user.display_name if current_user else "User"
                print(f"\n👋 Thanks for using MathsFun, {name}! Keep practicing!")
                return  # Exit application completely
            elif choice == "1":
                addition_mode(container, user.id)
            elif choice == "2":
                addition_tables_mode()
            elif choice == "3":
                # Sign out
                current_user = container.user_svc.get_current_user(supabase_client)
                name = current_user.display_name if current_user else "User"
                supabase_client.sign_out()
                print(f"\n👋 {name} has been signed out successfully!")
                print("Returning to authentication...\n")
                break  # Return to authentication flow
            else:
                print("❌ Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
