#!/usr/bin/env python3
"""Tests for UI layer functions using mocking strategy."""

import pytest
from ui import print_welcome, print_main_menu, get_user_input


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
        lines = output.strip().split('\n')
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
        mock_input = mocker.patch('builtins.input', return_value='test input')
        
        result = get_user_input("Enter something")
        
        assert result == "test input"
        mock_input.assert_called_once_with("Enter something: ")
    
    def test_get_user_input_with_default_used(self, mocker):
        """Test get_user_input with default value when user provides input."""
        mock_input = mocker.patch('builtins.input', return_value='user input')
        
        result = get_user_input("Enter something", "default")
        
        assert result == "user input"
        mock_input.assert_called_once_with("Enter something (default: default): ")
    
    def test_get_user_input_with_default_empty_input(self, mocker):
        """Test get_user_input with default value when user provides empty input."""
        mock_input = mocker.patch('builtins.input', return_value='')
        
        result = get_user_input("Enter something", "default")
        
        assert result == "default"
        mock_input.assert_called_once_with("Enter something (default: default): ")
    
    def test_get_user_input_with_default_whitespace_input(self, mocker):
        """Test get_user_input with default value when user provides whitespace."""
        mock_input = mocker.patch('builtins.input', return_value='   ')
        
        result = get_user_input("Enter something", "default")
        
        assert result == "default"
        mock_input.assert_called_once_with("Enter something (default: default): ")
    
    def test_get_user_input_strips_whitespace(self, mocker):
        """Test that user input is properly stripped of whitespace."""
        mock_input = mocker.patch('builtins.input', return_value='  test input  ')
        
        result = get_user_input("Enter something")
        
        assert result == "test input"
    
    @pytest.mark.parametrize("user_input,default,expected", [
        ("hello", None, "hello"),
        ("hello", "default", "hello"),
        ("", "default", "default"),
        ("   ", "default", "default"),
        ("123", "456", "123"),
        ("", None, ""),
    ])
    def test_get_user_input_various_scenarios(self, mocker, user_input, default, expected):
        """Test get_user_input with various input scenarios."""
        mock_input = mocker.patch('builtins.input', return_value=user_input)
        
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
        mock_input = mocker.patch('builtins.input', return_value='test')
        
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
        mock_input = mocker.patch('builtins.input', side_effect=['first', 'second', ''])
        
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
        from addition import display_difficulty_options
        
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
        from addition import get_difficulty_range
        
        # Mock user entering 2 for low, 4 for high
        mock_input = mocker.patch('ui.get_user_input', side_effect=['2', '4'])
        
        low, high = get_difficulty_range()
        
        assert low == 2
        assert high == 4
        assert mock_input.call_count == 2
    
    def test_get_difficulty_range_invalid_then_valid(self, mocker, capsys):
        """Test get_difficulty_range with invalid input followed by valid input."""
        from addition import get_difficulty_range
        
        # Mock user entering invalid, then valid input
        mock_input = mocker.patch('ui.get_user_input', side_effect=['0', '1', '6', '3'])
        
        low, high = get_difficulty_range()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert low == 1
        assert high == 3
        assert "❌ Please enter a number between 1 and 5" in output
        assert mock_input.call_count == 4
    
    def test_get_num_problems_valid(self, mocker):
        """Test get_num_problems with valid input."""
        from addition import get_num_problems
        
        mock_input = mocker.patch('ui.get_user_input', return_value='10')
        
        result = get_num_problems()
        
        assert result == 10
        mock_input.assert_called_once()
    
    def test_get_num_problems_unlimited(self, mocker):
        """Test get_num_problems with unlimited (0) input."""
        from addition import get_num_problems
        
        mock_input = mocker.patch('ui.get_user_input', return_value='0')
        
        result = get_num_problems()
        
        assert result == 0
        mock_input.assert_called_once()
    
    def test_get_num_problems_invalid_then_valid(self, mocker, capsys):
        """Test get_num_problems with invalid input followed by valid input."""
        from addition import get_num_problems
        
        mock_input = mocker.patch('ui.get_user_input', side_effect=['-5', 'abc', '5'])
        
        result = get_num_problems()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert result == 5
        assert "❌ Please enter 0 for unlimited or a positive number" in output
        assert "❌ Please enter a valid number" in output
        assert mock_input.call_count == 3