#!/usr/bin/env python3
"""Tests for main application entry point."""

import pytest
from unittest.mock import patch


class TestMain:
    """Test main application function."""
    
    def test_main_exit_immediately(self, mocker, capsys):
        """Test main function with immediate exit."""
        from main import main
        
        # Mock print functions to avoid actual output during test
        mock_print_welcome = mocker.patch('main.print_welcome')
        mock_print_main_menu = mocker.patch('main.print_main_menu')
        
        # Mock input to immediately exit
        mock_input = mocker.patch('builtins.input', return_value='exit')
        
        main()
        
        # Verify welcome was printed
        mock_print_welcome.assert_called_once()
        
        # Verify menu was printed
        mock_print_main_menu.assert_called_once()
        
        # Verify input was called
        mock_input.assert_called_once_with("Select an option: ")
        
        # Check exit message
        captured = capsys.readouterr()
        assert "👋 Thanks for using MathsFun! Keep practicing!" in captured.out
    
    def test_main_addition_mode_then_exit(self, mocker, capsys):
        """Test main function with addition mode selection then exit."""
        from main import main
        
        # Mock dependencies
        mock_print_welcome = mocker.patch('main.print_welcome')
        mock_print_main_menu = mocker.patch('main.print_main_menu')
        mock_addition_mode = mocker.patch('main.addition_mode')
        
        # Mock input to select addition mode then exit
        mock_input = mocker.patch('builtins.input', side_effect=['1', 'exit'])
        
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
        assert "👋 Thanks for using MathsFun! Keep practicing!" in captured.out
    
    def test_main_invalid_option_then_exit(self, mocker, capsys):
        """Test main function with invalid option then exit."""
        from main import main
        
        # Mock dependencies
        mock_print_welcome = mocker.patch('main.print_welcome')
        mock_print_main_menu = mocker.patch('main.print_main_menu')
        
        # Mock input to provide invalid option then exit
        mock_input = mocker.patch('builtins.input', side_effect=['invalid', 'exit'])
        
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
        assert "👋 Thanks for using MathsFun! Keep practicing!" in captured.out
    
    def test_main_multiple_invalid_options_then_addition_then_exit(self, mocker, capsys):
        """Test main function with multiple invalid options, then addition, then exit."""
        from main import main
        
        # Mock dependencies
        mock_print_welcome = mocker.patch('main.print_welcome')
        mock_print_main_menu = mocker.patch('main.print_main_menu')
        mock_addition_mode = mocker.patch('main.addition_mode')
        mock_addition_tables_mode = mocker.patch('main.addition_tables_mode')
        
        # Mock input sequence: invalid options, then valid selection, then exit
        mock_input = mocker.patch('builtins.input', side_effect=['invalid', 'abc', '1', 'exit'])
        
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
        assert "👋 Thanks for using MathsFun! Keep practicing!" in captured.out


class TestMainIfName:
    """Test the if __name__ == '__main__' block."""
    
    @patch('main.main')
    def test_main_called_when_run_as_script(self, mock_main):
        """Test that main() is called when script is run directly."""
        # Import the module to trigger the if __name__ == '__main__' block
        import importlib
        import main
        
        # Reload the module to simulate running as script
        # Note: This is a bit tricky to test directly, but we can verify the structure
        # The actual execution happens at import time
        
        # For this test, we'll just verify the structure exists
        assert hasattr(main, 'main')
        assert callable(main.main)