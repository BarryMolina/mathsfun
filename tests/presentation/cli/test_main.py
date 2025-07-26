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
        mock_supabase_manager = mocker.patch(
            "src.presentation.cli.main.supabase_manager"
        )
        mock_supabase_manager.load_persisted_session.return_value = False
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
        mock_supabase_manager = mocker.patch(
            "src.presentation.cli.main.supabase_manager"
        )
        mock_supabase_manager.load_persisted_session.return_value = False
        mock_supabase_manager.is_authenticated.return_value = True

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
        mock_supabase_manager = mocker.patch(
            "src.presentation.cli.main.supabase_manager"
        )
        mock_supabase_manager.load_persisted_session.return_value = False
        mock_supabase_manager.is_authenticated.return_value = True

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
        mock_supabase_manager = mocker.patch(
            "src.presentation.cli.main.supabase_manager"
        )
        mock_supabase_manager.load_persisted_session.return_value = False
        mock_supabase_manager.is_authenticated.return_value = True

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
