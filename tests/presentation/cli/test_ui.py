#!/usr/bin/env python3
"""Tests for UI layer functions using mocking strategy."""

import pytest
from unittest.mock import patch, Mock
from src.presentation.cli.ui import (
    print_welcome,
    print_main_menu,
    get_user_input,
    get_email_input,
    get_password_input,
    get_password_confirmation,
    print_authentication_menu,
    print_authentication_status,
    print_user_welcome,
)


class TestPrintWelcome:
    """Test the print_welcome function."""

    def test_print_welcome_output(self, capsys):
        """Test that welcome message is printed correctly."""
        print_welcome()

        captured = capsys.readouterr()
        output = captured.out

        # Check for key elements
        assert "🎯 Welcome to MathsFun! 🎯" in output
        assert "Let's make math practice fun and interactive!" in output
        assert "=" * 50 in output

        # Check structure
        lines = output.strip().split("\n")
        assert len(lines) >= 4  # Should have multiple lines

        # Check that it starts and ends with separator lines
        assert lines[0] == "=" * 50
        assert lines[-1] == "=" * 50


class TestPrintMainMenu:
    """Test the print_main_menu function."""

    def test_print_main_menu_output(self, capsys):
        """Test that main menu is printed correctly."""
        print_main_menu()

        captured = capsys.readouterr()
        output = captured.out

        # Check for menu elements
        assert "📚 Main Menu:" in output
        assert "1. Addition" in output
        assert "Type 'exit' to quit the application" in output
        assert "-" * 30 in output


class TestGetUserInput:
    """Test the get_user_input function with various scenarios."""

    def test_get_user_input_no_default(self, mocker):
        """Test get_user_input without default value."""
        mock_input = mocker.patch("builtins.input", return_value="test input")

        result = get_user_input("Enter something")

        assert result == "test input"
        mock_input.assert_called_once_with("Enter something: ")

    def test_get_user_input_with_default_used(self, mocker):
        """Test get_user_input with default value when user provides input."""
        mock_input = mocker.patch("builtins.input", return_value="user input")

        result = get_user_input("Enter something", "default")

        assert result == "user input"
        mock_input.assert_called_once_with("Enter something (default: default): ")

    def test_get_user_input_with_default_empty_input(self, mocker):
        """Test get_user_input with default value when user provides empty input."""
        mock_input = mocker.patch("builtins.input", return_value="")

        result = get_user_input("Enter something", "default")

        assert result == "default"
        mock_input.assert_called_once_with("Enter something (default: default): ")

    def test_get_user_input_with_default_whitespace_input(self, mocker):
        """Test get_user_input with default value when user provides whitespace."""
        mock_input = mocker.patch("builtins.input", return_value="   ")

        result = get_user_input("Enter something", "default")

        assert result == "default"
        mock_input.assert_called_once_with("Enter something (default: default): ")

    def test_get_user_input_strips_whitespace(self, mocker):
        """Test that user input is properly stripped of whitespace."""
        mock_input = mocker.patch("builtins.input", return_value="  test input  ")

        result = get_user_input("Enter something")

        assert result == "test input"

    @pytest.mark.parametrize(
        "user_input,default,expected",
        [
            ("hello", None, "hello"),
            ("hello", "default", "hello"),
            ("", "default", "default"),
            ("   ", "default", "default"),
            ("123", "456", "123"),
            ("", None, ""),
        ],
    )
    def test_get_user_input_various_scenarios(
        self, mocker, user_input, default, expected
    ):
        """Test get_user_input with various input scenarios."""
        mock_input = mocker.patch("builtins.input", return_value=user_input)

        if default is None:
            result = get_user_input("Test prompt")
            expected_call = "Test prompt: "
        else:
            result = get_user_input("Test prompt", default)
            expected_call = f"Test prompt (default: {default}): "

        assert result == expected
        mock_input.assert_called_once_with(expected_call)


class TestUIIntegration:
    """Integration tests for UI functions working together."""

    def test_ui_functions_dont_interfere(self, capsys, mocker):
        """Test that UI functions can be called in sequence without interference."""
        mock_input = mocker.patch("builtins.input", return_value="test")

        # Call multiple UI functions
        print_welcome()
        print_main_menu()
        result = get_user_input("Test")

        # Check that all functions worked
        captured = capsys.readouterr()
        output = captured.out

        assert "🎯 Welcome to MathsFun! 🎯" in output
        assert "📚 Main Menu:" in output
        assert result == "test"
        mock_input.assert_called_once()

    def test_multiple_input_calls(self, mocker):
        """Test multiple sequential input calls."""
        mock_input = mocker.patch("builtins.input", side_effect=["first", "second", ""])

        result1 = get_user_input("First prompt")
        result2 = get_user_input("Second prompt")
        result3 = get_user_input("Third prompt", "default")

        assert result1 == "first"
        assert result2 == "second"
        assert result3 == "default"

        assert mock_input.call_count == 3


# Tests specifically for UI behavior that might appear in addition.py
class TestUIInAddition:
    """Test UI-related functions that are defined in addition.py but use UI patterns."""

    def test_display_difficulty_options(self, capsys):
        """Test the display_difficulty_options function from addition.py."""
        from src.presentation.controllers.addition import display_difficulty_options

        display_difficulty_options()

        captured = capsys.readouterr()
        output = captured.out

        # Check for difficulty level display
        assert "🎚️  Difficulty Levels:" in output
        assert "1. Two single-digit numbers" in output
        assert "2. Two two-digit numbers, no carrying" in output
        assert "3. Two two-digit numbers with carrying" in output
        assert "4. Two three-digit numbers, no carrying" in output
        assert "5. Two three-digit numbers with carrying" in output

    def test_get_difficulty_range_valid_input(self, mocker):
        """Test get_difficulty_range with valid input."""
        from src.presentation.controllers.addition import get_difficulty_range

        # Mock user entering 2 for low, 4 for high
        mock_input = mocker.patch("builtins.input", side_effect=["2", "4"])

        low, high = get_difficulty_range()

        assert low == 2
        assert high == 4
        assert mock_input.call_count == 2

    def test_get_difficulty_range_invalid_then_valid(self, mocker, capsys):
        """Test get_difficulty_range with invalid input followed by valid input."""
        from src.presentation.controllers.addition import get_difficulty_range

        # Mock user entering invalid, then valid input
        mock_input = mocker.patch("builtins.input", side_effect=["0", "1", "6", "3"])

        low, high = get_difficulty_range()

        captured = capsys.readouterr()
        output = captured.out

        assert low == 1
        assert high == 3
        assert "❌ Please enter a number between 1 and 5" in output
        assert mock_input.call_count == 4

    def test_get_num_problems_valid(self, mocker):
        """Test get_num_problems with valid input."""
        from src.presentation.controllers.addition import get_num_problems

        mock_input = mocker.patch("builtins.input", return_value="10")

        result = get_num_problems()

        assert result == 10
        mock_input.assert_called_once()

    def test_get_num_problems_unlimited(self, mocker):
        """Test get_num_problems with unlimited (0) input."""
        from src.presentation.controllers.addition import get_num_problems

        mock_input = mocker.patch("builtins.input", return_value="0")

        result = get_num_problems()

        assert result == 0
        mock_input.assert_called_once()

    def test_get_num_problems_invalid_then_valid(self, mocker, capsys):
        """Test get_num_problems with invalid input followed by valid input."""
        from src.presentation.controllers.addition import get_num_problems

        mock_input = mocker.patch("builtins.input", side_effect=["-5", "abc", "5"])

        result = get_num_problems()

        captured = capsys.readouterr()
        output = captured.out

        assert result == 5
        assert "❌ Please enter 0 for unlimited or a positive number" in output
        assert "❌ Please enter a valid number" in output
        assert mock_input.call_count == 3


class TestPrintAuthenticationMenu:
    """Test the print_authentication_menu function."""

    def test_print_authentication_menu_output(self, capsys):
        """Test that authentication menu includes email/password options."""
        print_authentication_menu()

        captured = capsys.readouterr()
        output = captured.out

        # Check for authentication menu elements
        assert "🔐 Authentication Required" in output
        assert "1. Sign in with Google" in output
        assert "2. Sign in with email/password" in output
        assert "3. Sign up with email/password" in output
        assert "Type 'exit' to quit the application" in output
        assert "-" * 30 in output


class TestGetEmailInput:
    """Test the get_email_input function."""

    def test_get_email_input_valid_email(self, mocker):
        """Test get_email_input with valid email address."""
        mock_input = mocker.patch("builtins.input", return_value="test@example.com")

        result = get_email_input()

        assert result == "test@example.com"
        mock_input.assert_called_once_with("Email: ")

    def test_get_email_input_empty_then_valid(self, mocker, capsys):
        """Test get_email_input with empty input followed by valid email."""
        mock_input = mocker.patch(
            "builtins.input", side_effect=["", "test@example.com"]
        )

        result = get_email_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "test@example.com"
        assert "❌ Email cannot be empty. Please try again." in output
        assert mock_input.call_count == 2

    def test_get_email_input_invalid_format_then_valid(self, mocker, capsys):
        """Test get_email_input with invalid format followed by valid email."""
        mock_input = mocker.patch(
            "builtins.input", side_effect=["invalid-email", "test@example.com"]
        )

        result = get_email_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "test@example.com"
        assert "❌ Please enter a valid email address" in output
        assert mock_input.call_count == 2

    def test_get_email_input_multiple_invalid_formats(self, mocker, capsys):
        """Test get_email_input with multiple invalid formats."""
        mock_input = mocker.patch(
            "builtins.input",
            side_effect=[
                "plaintext",
                "@example.com",
                "test@",
                "test@example",
                "test@example.com",
            ],
        )

        result = get_email_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "test@example.com"
        assert output.count("❌ Please enter a valid email address") == 4
        assert mock_input.call_count == 5

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
            "a@b.co",
        ],
    )
    def test_get_email_input_valid_formats(self, mocker, email):
        """Test get_email_input with various valid email formats."""
        mock_input = mocker.patch("builtins.input", return_value=email)

        result = get_email_input()

        assert result == email
        mock_input.assert_called_once_with("Email: ")

    @pytest.mark.parametrize(
        "email",
        [
            "@example.com",
            "user@",
            "user.example.com",
            "user@example",
            "",
            "   ",
        ],
    )
    def test_get_email_input_invalid_formats(self, mocker, email):
        """Test get_email_input with various invalid email formats."""
        mock_input = mocker.patch(
            "builtins.input", side_effect=[email, "valid@example.com"]
        )

        result = get_email_input()

        assert result == "valid@example.com"
        assert mock_input.call_count == 2


class TestGetPasswordInput:
    """Test the get_password_input function."""

    def test_get_password_input_valid_password(self, mocker):
        """Test get_password_input with valid password."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass", return_value="password123"
        )

        result = get_password_input()

        assert result == "password123"
        mock_getpass.assert_called_once_with("Password: ")

    def test_get_password_input_custom_prompt(self, mocker):
        """Test get_password_input with custom prompt."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass", return_value="password123"
        )

        result = get_password_input("New password")

        assert result == "password123"
        mock_getpass.assert_called_once_with("New password: ")

    def test_get_password_input_empty_then_valid(self, mocker, capsys):
        """Test get_password_input with empty password followed by valid password."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass", side_effect=["", "password123"]
        )

        result = get_password_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "password123"
        assert "❌ Password cannot be empty. Please try again." in output
        assert mock_getpass.call_count == 2

    def test_get_password_input_too_short_then_valid(self, mocker, capsys):
        """Test get_password_input with password too short followed by valid password."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=["123", "password123"],
        )

        result = get_password_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "password123"
        assert (
            "❌ Password must be at least 6 characters long. Please try again."
            in output
        )
        assert mock_getpass.call_count == 2

    def test_get_password_input_multiple_invalid_attempts(self, mocker, capsys):
        """Test get_password_input with multiple invalid attempts."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=["", "12345", "password123"],
        )

        result = get_password_input()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "password123"
        assert "❌ Password cannot be empty. Please try again." in output
        assert (
            "❌ Password must be at least 6 characters long. Please try again."
            in output
        )
        assert mock_getpass.call_count == 3


class TestGetPasswordConfirmation:
    """Test the get_password_confirmation function."""

    def test_get_password_confirmation_matching_passwords(self, mocker):
        """Test get_password_confirmation with matching passwords."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=["password123", "password123"],
        )

        result = get_password_confirmation()

        assert result == "password123"
        assert mock_getpass.call_count == 2

    def test_get_password_confirmation_mismatched_then_matching(self, mocker, capsys):
        """Test get_password_confirmation with mismatched then matching passwords."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=["password123", "different", "newpassword", "newpassword"],
        )

        result = get_password_confirmation()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "newpassword"
        assert "❌ Passwords do not match. Please try again." in output
        assert mock_getpass.call_count == 4

    def test_get_password_confirmation_multiple_mismatches(self, mocker, capsys):
        """Test get_password_confirmation with multiple password mismatches."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=[
                "password1",
                "password2",
                "password3",
                "password4",
                "finalpass",
                "finalpass",
            ],
        )

        result = get_password_confirmation()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "finalpass"
        assert output.count("❌ Passwords do not match. Please try again.") == 2
        assert mock_getpass.call_count == 6

    def test_get_password_confirmation_empty_password_validation(self, mocker, capsys):
        """Test get_password_confirmation handles empty password validation."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=[
                "",  # Empty password
                "123456",  # Valid password
                "123456",  # Matching confirmation
            ],
        )

        result = get_password_confirmation()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "123456"
        assert "❌ Password cannot be empty. Please try again." in output
        assert mock_getpass.call_count == 3

    def test_get_password_confirmation_short_password_validation(self, mocker, capsys):
        """Test get_password_confirmation handles short password validation."""
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=[
                "123",  # Too short
                "123456",  # Valid password
                "123456",  # Matching confirmation
            ],
        )

        result = get_password_confirmation()

        captured = capsys.readouterr()
        output = captured.out

        assert result == "123456"
        assert (
            "❌ Password must be at least 6 characters long. Please try again."
            in output
        )
        assert mock_getpass.call_count == 3


class TestEmailPasswordUIIntegration:
    """Integration tests for email/password UI functions."""

    def test_email_password_signup_flow(self, mocker, capsys):
        """Test complete email/password signup UI flow."""
        mock_input = mocker.patch("builtins.input", return_value="test@example.com")
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass",
            side_effect=["password123", "password123"],
        )

        email = get_email_input()
        password = get_password_confirmation()

        assert email == "test@example.com"
        assert password == "password123"
        mock_input.assert_called_once()
        assert mock_getpass.call_count == 2

    def test_email_password_signin_flow(self, mocker):
        """Test complete email/password signin UI flow."""
        mock_input = mocker.patch("builtins.input", return_value="user@example.com")
        mock_getpass = mocker.patch(
            "src.presentation.cli.ui.getpass.getpass", return_value="mypassword"
        )

        email = get_email_input()
        password = get_password_input()

        assert email == "user@example.com"
        assert password == "mypassword"
        mock_input.assert_called_once()
        mock_getpass.assert_called_once()


class TestPrintAuthenticationStatus:
    """Test the print_authentication_status function."""

    def test_print_authentication_status_success(self, capsys):
        """Test print_authentication_status with success=True."""
        print_authentication_status("Login successful", success=True)

        captured = capsys.readouterr()
        output = captured.out

        assert "✅ Login successful" in output

    def test_print_authentication_status_failure(self, capsys):
        """Test print_authentication_status with success=False."""
        print_authentication_status("Login failed", success=False)

        captured = capsys.readouterr()
        output = captured.out

        assert "❌ Login failed" in output

    def test_print_authentication_status_default_success(self, capsys):
        """Test print_authentication_status with default success=True."""
        print_authentication_status("Operation completed")

        captured = capsys.readouterr()
        output = captured.out

        assert "✅ Operation completed" in output


class TestPrintUserWelcome:
    """Test the print_user_welcome function."""

    def test_print_user_welcome_full_data(self, capsys):
        """Test print_user_welcome with all user data fields."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        print_user_welcome(user_data)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Welcome back, John Doe!" in output
        assert "📧 Signed in as: john@example.com" in output
        assert "🖼️  Profile picture: https://example.com/avatar.jpg" in output
        assert "-" * 50 in output

    def test_print_user_welcome_minimal_data(self, capsys):
        """Test print_user_welcome with minimal user data."""
        user_data = {"email": "test@example.com"}

        print_user_welcome(user_data)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Welcome back, User!" in output
        assert "📧 Signed in as: test@example.com" in output
        assert "🖼️  Profile picture:" not in output
        assert "-" * 50 in output

    def test_print_user_welcome_empty_data(self, capsys):
        """Test print_user_welcome with empty user data."""
        user_data = {}

        print_user_welcome(user_data)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Welcome back, User!" in output
        assert "📧 Signed in as: " in output
        assert "🖼️  Profile picture:" not in output
        assert "-" * 50 in output

    def test_print_user_welcome_no_avatar(self, capsys):
        """Test print_user_welcome with name and email but no avatar."""
        user_data = {"name": "Jane Smith", "email": "jane@example.com"}

        print_user_welcome(user_data)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Welcome back, Jane Smith!" in output
        assert "📧 Signed in as: jane@example.com" in output
        assert "🖼️  Profile picture:" not in output
        assert "-" * 50 in output
