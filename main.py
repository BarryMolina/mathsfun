#!/usr/bin/env python3
from ui import print_welcome, print_main_menu
from addition import addition_mode


def main():
    """Main application loop"""
    print_welcome()

    while True:
        print_main_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == "exit":
            print("\n👋 Thanks for using MathsFun! Keep practicing!")
            break
        elif choice == "1":
            addition_mode()
        else:
            print("❌ Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
