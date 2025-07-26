#!/usr/bin/env python3
"""Tests for session management functions."""

import pytest
from src.presentation.controllers.session import (
    format_duration,
    show_results,
    prompt_start_session,
)


class TestFormatDuration:
    """Test the format_duration function."""

    def test_seconds_only(self):
        """Test formatting for durations under 60 seconds."""
        assert format_duration(30.5) == "30.5 seconds"
        assert format_duration(59.9) == "59.9 seconds"
        assert format_duration(0.1) == "0.1 seconds"

    def test_minutes_and_seconds(self):
        """Test formatting for durations between 1-60 minutes."""
        assert format_duration(90.5) == "1m 30.5s"
        assert format_duration(125.0) == "2m 5.0s"
        assert format_duration(3599.9) == "59m 59.9s"

    def test_hours_minutes_seconds(self):
        """Test formatting for durations over 1 hour."""
        assert format_duration(3661.5) == "1h 1m 1.5s"
        assert format_duration(7200.0) == "2h 0m 0.0s"
        assert format_duration(3665.2) == "1h 1m 5.2s"

    def test_edge_cases(self):
        """Test edge cases and boundary values."""
        assert format_duration(60.0) == "1m 0.0s"
        assert format_duration(3600.0) == "1h 0m 0.0s"
        assert format_duration(0.0) == "0.0 seconds"


class TestShowResults:
    """Test the show_results function."""

    def test_show_results_unlimited_session(self, capsys, unlimited_generator):
        """Test results display for unlimited session."""
        show_results(8, 10, 125.5, unlimited_generator)

        captured = capsys.readouterr()
        output = captured.out

        # Check for key elements in output
        assert "🎉 Session Complete! 🎉" in output
        assert "Session ended by user" in output
        assert "Problems presented: 10" in output
        assert "Correct answers: 8" in output
        assert "Total attempted: 10" in output
        assert "Skipped: 0" in output
        assert "Time taken: 2m 5.5s" in output
        assert "Accuracy: 80.0%" in output
        assert "🎊 Excellent work! Keep it up!" in output

    def test_show_results_limited_session_completed(self, capsys, mock_generator):
        """Test results display for completed limited session."""
        mock_generator.get_total_generated.return_value = 5
        mock_generator.num_problems = 5

        show_results(5, 5, 60.0, mock_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Quiz Complete! 🎉" in output
        assert "All problems completed" in output
        assert "Accuracy: 100.0%" in output
        assert "🌟 Outstanding! You're a math superstar!" in output

    def test_show_results_limited_session_stopped(self, capsys, mock_generator):
        """Test results display for stopped limited session."""
        show_results(2, 3, 45.0, mock_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert "🎉 Session Complete! 🎉" in output
        assert "Session ended by user" in output
        assert "Skipped: 0" in output

    def test_show_results_no_attempts(self, capsys, mock_generator):
        """Test results display when no problems were attempted."""
        show_results(0, 0, 10.0, mock_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert "🤔 No problems attempted this time." in output
        assert "Accuracy:" not in output

    @pytest.mark.parametrize(
        "correct,total,expected_message",
        [
            (9, 10, "🌟 Outstanding! You're a math superstar!"),
            (8, 10, "🎊 Excellent work! Keep it up!"),
            (7, 10, "👍 Good job! Practice makes perfect!"),
            (6, 10, "💪 Keep practicing! You'll get better!"),
        ],
    )
    def test_accuracy_messages(
        self, capsys, mock_generator, correct, total, expected_message
    ):
        """Test different accuracy threshold messages."""
        show_results(correct, total, 60.0, mock_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert expected_message in output


class TestPromptStartSession:
    """Test the prompt_start_session function."""

    def test_prompt_unlimited_session(self, capsys, mocker, unlimited_generator):
        """Test prompt for unlimited session."""
        mock_input = mocker.patch("builtins.input", return_value="")

        prompt_start_session(unlimited_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert "✅ Ready to start unlimited session!" in output
        assert "Solve problems until you're ready to stop." in output
        assert "Press Enter when you're ready to start" in output
        mock_input.assert_called_once()

    def test_prompt_limited_session(self, capsys, mocker, mock_generator):
        """Test prompt for limited session."""
        mock_input = mocker.patch("builtins.input", return_value="")

        prompt_start_session(mock_generator)

        captured = capsys.readouterr()
        output = captured.out

        assert (
            f"✅ Ready to start! {mock_generator.num_problems} problems prepared."
            in output
        )
        assert "Press Enter when you're ready to start" in output
        mock_input.assert_called_once()
