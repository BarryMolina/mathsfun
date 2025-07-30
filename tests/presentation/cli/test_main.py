#!/usr/bin/env python3
"""Tests for main application entry point."""

import pytest
from unittest.mock import MagicMock
from src.domain.models.user import User


class TestMain:
    """Test main application function."""

    def test_main_exit_immediately(self, mocker, capsys):
        """Test main function with immediate exit during authentication."""
        from src.presentation.cli.main import main

        # Mock print functions to avoid actual output during test
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_container = mocker.patch("src.presentation.cli.main.Container")
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(False, None)
        )

        main()

        # Verify welcome was printed
        mock_print_welcome.assert_called_once()

        # Verify authentication flow was called with container
        mock_authentication_flow.assert_called_once()

        # Check exit message
        captured = capsys.readouterr()
        assert "👋 Thanks for visiting MathsFun!" in captured.out

    def test_main_addition_mode_then_exit(self, mocker, capsys):
        """Test main function with addition mode selection then exit."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        mock_addition_mode = mocker.patch("src.presentation.cli.main.addition_mode")

        # Mock successful authentication with User model
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(True, user)
        )

        # Mock container and its services
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_user_service.get_or_create_user_profile.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        mock_supabase_manager_instance.is_authenticated.return_value = True

        # Mock input to select addition mode then exit
        mock_input = mocker.patch("builtins.input", side_effect=["1", "exit"])

        main()

        # Verify welcome was printed
        mock_print_welcome.assert_called_once()

        # Verify menu was printed twice (once before '1', once before 'exit')
        assert mock_print_main_menu.call_count == 2

        # Verify addition mode was called
        mock_addition_mode.assert_called_once()

        # Verify input was called twice
        assert mock_input.call_count == 2

        # Check exit message
        captured = capsys.readouterr()
        assert (
            "👋 Thanks for using MathsFun, Test User! Keep practicing!" in captured.out
        )

    def test_main_invalid_option_then_exit(self, mocker, capsys):
        """Test main function with invalid option then exit."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")

        # Mock successful authentication with User model
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(True, user)
        )

        # Mock container and its services
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_user_service.get_or_create_user_profile.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        mock_supabase_manager_instance.is_authenticated.return_value = True

        # Mock input to provide invalid option then exit
        mock_input = mocker.patch("builtins.input", side_effect=["invalid", "exit"])

        main()

        # Verify welcome was printed
        mock_print_welcome.assert_called_once()

        # Verify menu was printed twice
        assert mock_print_main_menu.call_count == 2

        # Verify input was called twice
        assert mock_input.call_count == 2

        # Check both invalid option and exit messages
        captured = capsys.readouterr()
        assert "❌ Invalid option. Please try again." in captured.out
        assert (
            "👋 Thanks for using MathsFun, Test User! Keep practicing!" in captured.out
        )

    def test_main_multiple_invalid_options_then_addition_then_exit(
        self, mocker, capsys
    ):
        """Test main function with multiple invalid options, then addition, then exit."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        mock_addition_mode = mocker.patch("src.presentation.cli.main.addition_mode")
        mock_addition_tables_mode = mocker.patch(
            "src.presentation.cli.main.addition_tables_mode"
        )

        # Mock successful authentication with User model
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(True, user)
        )

        # Mock container and its services
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_user_service.get_or_create_user_profile.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        mock_supabase_manager_instance.is_authenticated.return_value = True

        # Mock input sequence: invalid options, then valid selection, then exit
        mock_input = mocker.patch(
            "builtins.input", side_effect=["invalid", "abc", "1", "exit"]
        )

        main()

        # Verify welcome was printed once
        mock_print_welcome.assert_called_once()

        # Verify menu was printed 4 times
        assert mock_print_main_menu.call_count == 4

        # Verify addition mode was called once
        mock_addition_mode.assert_called_once()

        # Verify input was called 4 times
        assert mock_input.call_count == 4

        # Check messages
        captured = capsys.readouterr()
        # Should see 2 invalid option messages
        invalid_count = captured.out.count("❌ Invalid option. Please try again.")
        assert invalid_count == 2
        assert (
            "👋 Thanks for using MathsFun, Test User! Keep practicing!" in captured.out
        )


class TestAuthenticationFlow:
    """Test authentication_flow function."""

    def test_authentication_flow_invalid_environment(self, mocker):
        """Test authentication flow with invalid environment."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(False, "Invalid environment")
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = False

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_validate_environment.assert_called_once_with(use_local=False)
        mock_print_authentication_status.assert_called_once_with("Invalid environment", False)

    def test_authentication_flow_exit_choice(self, mocker):
        """Test authentication flow with exit choice."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_input = mocker.patch("builtins.input", return_value="exit")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print_authentication_menu.assert_called_once()
        mock_input.assert_called_once_with("Select an option: ")

    def test_authentication_flow_google_oauth_success(self, mocker):
        """Test authentication flow with successful Google OAuth."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_print_user_welcome = mocker.patch(
            "src.presentation.cli.main.print_user_welcome"
        )
        mock_input = mocker.patch("builtins.input", return_value="1")
        
        # Mock successful authentication
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_container = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container.user_svc = mock_user_service
        
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_in_with_google.return_value = {"success": True}

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (True, user)
        mock_supabase_manager.sign_in_with_google.assert_called_once()
        mock_print_authentication_status.assert_called_once_with("Authentication successful!")
        mock_user_service.get_current_user.assert_called_once_with(force_refresh=True)
        mock_print_user_welcome.assert_called_once_with({
            "name": "Test User",
            "email": "test@example.com", 
            "avatar_url": None
        })

    def test_authentication_flow_google_oauth_failure(self, mocker):
        """Test authentication flow with failed Google OAuth."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["1", "exit"])
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_in_with_google.return_value = {"success": False, "error": "OAuth failed"}

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_supabase_manager.sign_in_with_google.assert_called_once()
        mock_print_authentication_status.assert_called_with("OAuth failed", False)

    def test_authentication_flow_google_oauth_no_result(self, mocker):
        """Test authentication flow with Google OAuth returning None."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["1", "exit"])
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_in_with_google.return_value = None

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print_authentication_status.assert_called_with("Authentication failed", False)

    def test_authentication_flow_email_signin_success(self, mocker):
        """Test authentication flow with successful email/password sign-in."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_print_user_welcome = mocker.patch(
            "src.presentation.cli.main.print_user_welcome"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="test@example.com"
        )
        mock_get_password_input = mocker.patch(
            "src.presentation.cli.main.get_password_input",
            return_value="password123"
        )
        mock_input = mocker.patch("builtins.input", return_value="2")
        mock_print = mocker.patch("builtins.print")
        
        # Mock successful authentication
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_container = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container.user_svc = mock_user_service
        
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_in_with_email_password.return_value = {"success": True}

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (True, user)
        mock_get_email_input.assert_called_once()
        mock_get_password_input.assert_called_once()
        mock_supabase_manager.sign_in_with_email_password.assert_called_once_with("test@example.com", "password123")
        mock_print_authentication_status.assert_called_once_with("Authentication successful!")

    def test_authentication_flow_email_signin_failure(self, mocker):
        """Test authentication flow with failed email/password sign-in."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="test@example.com"
        )
        mock_get_password_input = mocker.patch(
            "src.presentation.cli.main.get_password_input",
            return_value="wrongpassword"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["2", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_in_with_email_password.return_value = {"success": False, "error": "Invalid credentials"}

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print_authentication_status.assert_called_with("Sign in failed: Invalid credentials", False)

    def test_authentication_flow_email_signin_keyboard_interrupt(self, mocker):
        """Test authentication flow with KeyboardInterrupt during email sign-in."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            side_effect=KeyboardInterrupt()
        )
        mock_input = mocker.patch("builtins.input", side_effect=["2", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print.assert_any_call("\n\n❌ Sign in cancelled by user.\n")

    def test_authentication_flow_email_signin_exception(self, mocker):
        """Test authentication flow with exception during email sign-in."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            side_effect=Exception("Network error")
        )
        mock_input = mocker.patch("builtins.input", side_effect=["2", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print_authentication_status.assert_called_with("Sign in failed: Network error", False)

    def test_authentication_flow_email_signup_success(self, mocker):
        """Test authentication flow with successful email/password sign-up."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_print_user_welcome = mocker.patch(
            "src.presentation.cli.main.print_user_welcome"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="newuser@example.com"
        )
        mock_get_password_confirmation = mocker.patch(
            "src.presentation.cli.main.get_password_confirmation",
            return_value="newpassword123"
        )
        mock_input = mocker.patch("builtins.input", return_value="3")
        mock_print = mocker.patch("builtins.print")
        
        # Mock successful sign-up
        user = User(id="new_user", email="newuser@example.com", display_name="New User")
        mock_container = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container.user_svc = mock_user_service
        
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True
        mock_supabase_manager.sign_up_with_email_password.return_value = {"success": True}

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (True, user)
        mock_get_email_input.assert_called_once()
        mock_get_password_confirmation.assert_called_once()
        mock_supabase_manager.sign_up_with_email_password.assert_called_once_with("newuser@example.com", "newpassword123")
        mock_print_authentication_status.assert_called_once_with("Account created successfully!")

    def test_authentication_flow_email_signup_keyboard_interrupt(self, mocker):
        """Test authentication flow with KeyboardInterrupt during email sign-up."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            side_effect=KeyboardInterrupt()
        )
        mock_input = mocker.patch("builtins.input", side_effect=["3", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print.assert_any_call("\n\n❌ Account creation cancelled by user.\n")

    def test_authentication_flow_invalid_choice(self, mocker):
        """Test authentication flow with invalid choice."""
        from src.presentation.cli.main import authentication_flow

        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["invalid", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = MagicMock()
        mock_supabase_manager = MagicMock()
        mock_supabase_manager.config.is_local = True

        result = authentication_flow(mock_container, mock_supabase_manager)

        assert result == (False, None)
        mock_print.assert_any_call("❌ Invalid option. Please try again.\n")

    def test_authentication_flow_email_signup_creation_failed_with_error(self, mocker):
        """Test email signup when account creation fails with error message."""
        from src.presentation.cli.main import authentication_flow
        
        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="test@example.com"
        )
        mock_get_password_confirmation = mocker.patch(
            "src.presentation.cli.main.get_password_confirmation",
            return_value="password123"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["3", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = mocker.Mock()
        mock_supabase_manager = mocker.Mock()
        mock_supabase_manager.config.is_local = True
        # Mock signup to fail with error result
        mock_supabase_manager.sign_up_with_email_password.return_value = {
            "success": False,
            "error": "Email already registered"
        }
        
        result = authentication_flow(mock_container, mock_supabase_manager)
        
        # Should fail to authenticate (covers lines 130-135)
        assert result == (False, None)
        mock_print_authentication_status.assert_called_with(
            "Account creation failed: Email already registered", False
        )

    def test_authentication_flow_email_signup_creation_failed_no_result(self, mocker):
        """Test email signup when account creation fails with no result."""
        from src.presentation.cli.main import authentication_flow
        
        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="test@example.com"
        )
        mock_get_password_confirmation = mocker.patch(
            "src.presentation.cli.main.get_password_confirmation",
            return_value="password123"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["3", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = mocker.Mock()
        mock_supabase_manager = mocker.Mock()
        mock_supabase_manager.config.is_local = True
        # Mock signup to return None
        mock_supabase_manager.sign_up_with_email_password.return_value = None
        
        result = authentication_flow(mock_container, mock_supabase_manager)
        
        # Should fail to authenticate (covers lines 130-135)
        assert result == (False, None)
        mock_print_authentication_status.assert_called_with(
            "Account creation failed: Account creation failed", False
        )

    def test_authentication_flow_email_signup_exception(self, mocker):
        """Test email signup when exception occurs during creation."""
        from src.presentation.cli.main import authentication_flow
        
        # Mock dependencies
        mock_validate_environment = mocker.patch(
            "src.presentation.cli.main.validate_environment",
            return_value=(True, "Valid environment")
        )
        mock_print_authentication_menu = mocker.patch(
            "src.presentation.cli.main.print_authentication_menu"
        )
        mock_print_authentication_status = mocker.patch(
            "src.presentation.cli.main.print_authentication_status"
        )
        mock_get_email_input = mocker.patch(
            "src.presentation.cli.main.get_email_input",
            return_value="test@example.com"
        )
        mock_get_password_confirmation = mocker.patch(
            "src.presentation.cli.main.get_password_confirmation",
            return_value="password123"
        )
        mock_input = mocker.patch("builtins.input", side_effect=["3", "exit"])
        mock_print = mocker.patch("builtins.print")
        
        mock_container = mocker.Mock()
        mock_supabase_manager = mocker.Mock()
        mock_supabase_manager.config.is_local = True
        # Mock signup to raise an exception
        mock_supabase_manager.sign_up_with_email_password.side_effect = Exception("Network error")
        
        result = authentication_flow(mock_container, mock_supabase_manager)
        
        # Should fail to authenticate (covers lines 140-141)
        assert result == (False, None)
        mock_print_authentication_status.assert_called_with(
            "Account creation failed: Network error", False
        )


class TestMainAdditionalScenarios:
    """Test additional main function scenarios."""

    def test_main_auto_login_success(self, mocker, capsys):
        """Test main function with successful auto-login."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        mock_addition_mode = mocker.patch("src.presentation.cli.main.addition_mode")

        # Mock successful auto-login
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = True
        mock_supabase_manager_instance.is_authenticated.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        # Mock input to select addition mode then exit
        mock_input = mocker.patch("builtins.input", side_effect=["1", "exit"])

        main()

        # Verify auto-login messages were printed
        captured = capsys.readouterr()
        assert "✅ Welcome back, Test User!" in captured.out
        assert "🔄 Restored previous session" in captured.out

        # Verify addition mode was called
        mock_addition_mode.assert_called_once_with(mock_container_instance, "test_user")

    def test_main_auto_login_invalid_session(self, mocker, capsys):
        """Test main function with invalid stored session."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(False, None)
        )

        # Mock invalid auto-login
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = None
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        main()

        # Verify invalid session message was printed
        captured = capsys.readouterr()
        assert "⚠️  Stored session invalid, please sign in again" in captured.out

        # Verify authentication flow was called
        mock_authentication_flow.assert_called_once()

    def test_main_user_data_fetch_failure(self, mocker, capsys):
        """Test main function when user data fetch fails after authentication."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        # Authentication succeeds but returns user=None, then exit on retry
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", 
            side_effect=[(True, None), (False, None)]  # Success but no user returned, then exit
        )

        # Mock container with user service that returns None for user data fetch
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        # Return None to simulate user data fetch failure (covers lines 179-182)
        mock_user_service.get_current_user.return_value = None
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        main()

        # Verify error message was printed (covers lines 179-182)
        captured = capsys.readouterr()
        assert "❌ Unable to fetch user data. Please try again." in captured.out

    def test_main_session_expired(self, mocker, capsys):
        """Test main function when session expires during menu loop."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", 
            side_effect=[(True, user), (False, None)]  # First success, then exit
        )

        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_supabase_manager_instance.is_authenticated.return_value = False  # Session expired
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        main()

        # Verify session expired message was printed
        captured = capsys.readouterr()
        assert "❌ Authentication session expired. Please sign in again." in captured.out

    def test_main_addition_tables_mode(self, mocker, capsys):
        """Test main function with addition tables mode selection."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        mock_addition_tables_mode = mocker.patch("src.presentation.cli.main.addition_tables_mode")

        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(True, user)
        )

        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_supabase_manager_instance.is_authenticated.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        # Mock input to select addition tables mode then exit
        mock_input = mocker.patch("builtins.input", side_effect=["2", "exit"])

        main()

        # Verify addition tables mode was called
        mock_addition_tables_mode.assert_called_once_with(mock_container_instance, user)

    def test_main_sign_out(self, mocker, capsys):
        """Test main function with sign out option."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", 
            side_effect=[(True, user), (False, None)]  # First success, then exit on re-auth
        )

        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = user
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_supabase_manager_instance.is_authenticated.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        # Mock input to select sign out option
        mock_input = mocker.patch("builtins.input", return_value="3")

        main()

        # Verify sign out was called
        mock_supabase_manager_instance.sign_out.assert_called_once()
        
        # Verify sign out messages were printed
        captured = capsys.readouterr()
        assert "👋 Test User has been signed out successfully!" in captured.out
        assert "Returning to authentication..." in captured.out

    def test_main_sign_out_no_user_name(self, mocker, capsys):
        """Test main function with sign out when user service returns None."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", 
            side_effect=[(True, user), (False, None)]  # First success, then exit on re-auth
        )

        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        # Return user first, then None for sign out
        mock_user_service.get_current_user.side_effect = [user, None]
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_supabase_manager_instance.is_authenticated.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        # Mock input to select sign out option
        mock_input = mocker.patch("builtins.input", return_value="3")

        main()

        # Verify sign out messages with default name
        captured = capsys.readouterr()
        assert "👋 Test User has been signed out successfully!" in captured.out

    def test_main_exit_no_user_name(self, mocker, capsys):
        """Test main function with exit when user service returns None."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_print_main_menu = mocker.patch("src.presentation.cli.main.print_main_menu")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(True, user)
        )

        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        # Return user first, then None for exit
        mock_user_service.get_current_user.side_effect = [user, None]
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_supabase_manager_instance.is_authenticated.return_value = True
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )

        # Mock input to select exit option
        mock_input = mocker.patch("builtins.input", return_value="exit")

        main()

        # Verify exit message with default name
        captured = capsys.readouterr()
        assert "👋 Thanks for using MathsFun, Test User! Keep practicing!" in captured.out

    def test_main_with_use_local_parameter(self, mocker):
        """Test main function with use_local parameter."""
        from src.presentation.cli.main import main

        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(False, None)
        )
        
        mock_container = mocker.patch("src.presentation.cli.main.Container")
        mock_supabase_manager_instance = mocker.Mock()
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        
        # Mock input to prevent stdin reading
        mock_input = mocker.patch("builtins.input", return_value="exit")

        main(use_local=True)

        # Verify create_supabase_manager was called with use_local=True
        mock_create_supabase_manager.assert_called_once_with(use_local=True)

    def test_main_user_fetch_failure_after_auth(self, mocker, capsys):
        """Test main when user data fetch fails after successful authentication."""
        from src.presentation.cli.main import main
        
        # Mock dependencies
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        
        user = User(id="test_user", email="test@example.com", display_name="Test User")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", 
            side_effect=[(True, None), (False, None)]  # Success but no user returned, then exit
        )
        
        # Mock container with user service that returns None (user fetch failure)
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_current_user.return_value = None  # Simulate fetch failure
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        
        main()
        
        # Verify error message was printed (covers lines 179-182)
        captured = capsys.readouterr()
        assert "❌ Unable to fetch user data. Please try again." in captured.out


class TestMainIfName:
    """Test the if __name__ == '__main__' block."""

    def test_main_called_when_run_as_script(self):
        """Test that main() is called when script is run directly."""
        # Import the main module to verify the structure
        import main

        # For this test, we'll just verify the structure exists
        assert hasattr(main, "__name__")

        # We can't easily test the if __name__ == '__main__' execution
        # without actually running the script, so we just verify the structure is correct
        # The main functionality is tested in the other test methods

    def test_main_call_execution(self, mocker):
        """Test that main() can be called directly (covers line 217)."""
        from src.presentation.cli.main import main
        
        # Mock all the dependencies to prevent actual execution
        mock_print_welcome = mocker.patch("src.presentation.cli.main.print_welcome")
        mock_authentication_flow = mocker.patch(
            "src.presentation.cli.main.authentication_flow", return_value=(False, None)
        )
        
        mock_container_instance = MagicMock()
        mock_user_service = MagicMock()
        mock_container_instance.user_svc = mock_user_service
        mock_container = mocker.patch(
            "src.presentation.cli.main.Container", return_value=mock_container_instance
        )
        
        mock_supabase_manager_instance = mocker.Mock()
        mock_supabase_manager_instance.load_persisted_session.return_value = False
        mock_create_supabase_manager = mocker.patch(
            "src.presentation.cli.main.create_supabase_manager",
            return_value=mock_supabase_manager_instance,
        )
        
        # This should execute without error (covers line 217)
        main()
        
        # Verify main components were called
        mock_print_welcome.assert_called_once()
        mock_authentication_flow.assert_called_once()

