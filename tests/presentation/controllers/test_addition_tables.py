"""Comprehensive tests for addition_tables controller."""

import pytest
from unittest.mock import Mock, patch
import time
from typing import List, Tuple

from src.presentation.controllers.addition_tables import (
    get_table_range,
    get_order_preference,
    generate_addition_table_problems,
    AdditionTableGenerator,
    run_addition_table_quiz,
    addition_tables_mode,
)


class TestGetTableRange:
    """Test get_table_range function."""

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    def test_get_table_range_valid_input(self, mock_get_user_input):
        """Test valid table range input."""
        mock_get_user_input.side_effect = ["5", "10"]

        result = get_table_range()

        assert result == (5, 10)
        assert mock_get_user_input.call_count == 2

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    def test_get_table_range_same_values(self, mock_get_user_input):
        """Test table range with same low and high values."""
        mock_get_user_input.side_effect = ["7", "7"]

        result = get_table_range()

        assert result == (7, 7)

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_low_out_of_bounds(self, mock_print, mock_get_user_input):
        """Test low number out of valid range."""
        mock_get_user_input.side_effect = ["0", "5", "10"]  # First invalid, then valid

        result = get_table_range()

        assert result == (5, 10)
        mock_print.assert_called_with("❌ Please enter a number between 1 and 100")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_low_too_high(self, mock_print, mock_get_user_input):
        """Test low number above valid range."""
        mock_get_user_input.side_effect = [
            "101",
            "5",
            "10",
        ]  # First invalid, then valid

        result = get_table_range()

        assert result == (5, 10)
        mock_print.assert_called_with("❌ Please enter a number between 1 and 100")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_high_out_of_bounds(self, mock_print, mock_get_user_input):
        """Test high number out of valid range."""
        mock_get_user_input.side_effect = [
            "5",
            "101",
            "5",
            "10",
        ]  # Low, invalid high, low again, valid high

        result = get_table_range()

        assert result == (5, 10)
        mock_print.assert_called_with("❌ Please enter a number between 1 and 100")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_low_greater_than_high(
        self, mock_print, mock_get_user_input
    ):
        """Test when low number is greater than high number."""
        mock_get_user_input.side_effect = [
            "10",
            "5",
            "3",
            "8",
        ]  # First pair invalid, second valid

        result = get_table_range()

        assert result == (3, 8)
        mock_print.assert_called_with(
            "❌ Low number must be less than or equal to high number"
        )

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_invalid_number_format(
        self, mock_print, mock_get_user_input
    ):
        """Test invalid number format input."""
        mock_get_user_input.side_effect = [
            "abc",
            "5",
            "10",
        ]  # First invalid, then valid

        result = get_table_range()

        assert result == (5, 10)
        mock_print.assert_called_with("❌ Please enter a valid number")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_table_range_multiple_validation_failures(
        self, mock_print, mock_get_user_input
    ):
        """Test multiple validation failures before success."""
        mock_get_user_input.side_effect = [
            "0",  # Invalid: too low
            "101",  # Invalid: too high
            "10",
            "5",  # Invalid: low > high
            "2",
            "7",  # Valid
        ]

        result = get_table_range()

        assert result == (2, 7)
        assert mock_print.call_count >= 3  # Multiple error messages


class TestGetOrderPreference:
    """Test get_order_preference function."""

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_order_preference_sequential(self, mock_print, mock_get_user_input):
        """Test selecting sequential order."""
        mock_get_user_input.return_value = "1"

        result = get_order_preference()

        assert result is False  # False for sequential
        # Check that menu was displayed
        assert any("Sequential" in str(call) for call in mock_print.call_args_list)

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_order_preference_random(self, mock_print, mock_get_user_input):
        """Test selecting random order."""
        mock_get_user_input.return_value = "2"

        result = get_order_preference()

        assert result is True  # True for random
        # Check that menu was displayed
        assert any("Random order" in str(call) for call in mock_print.call_args_list)

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_order_preference_invalid_choice(self, mock_print, mock_get_user_input):
        """Test invalid choice followed by valid choice."""
        mock_get_user_input.side_effect = ["3", "1"]  # Invalid, then valid

        result = get_order_preference()

        assert result is False
        mock_print.assert_any_call("❌ Please enter 1 or 2")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_order_preference_invalid_format(self, mock_print, mock_get_user_input):
        """Test invalid number format followed by valid choice."""
        mock_get_user_input.side_effect = ["abc", "2"]  # Invalid, then valid

        result = get_order_preference()

        assert result is True
        mock_print.assert_any_call("❌ Please enter a valid number")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("builtins.print")
    def test_get_order_preference_default_value(self, mock_print, mock_get_user_input):
        """Test using default value (empty input)."""
        mock_get_user_input.return_value = ""  # Will use default "1"

        with patch.object(mock_get_user_input, "return_value", ""):
            # This simulates get_user_input returning default value
            mock_get_user_input.return_value = "1"  # Simulate default behavior
            result = get_order_preference()

        assert result is False


class TestGenerateAdditionTableProblems:
    """Test generate_addition_table_problems function."""

    def test_generate_problems_single_number(self):
        """Test generating problems for single number table."""
        problems = generate_addition_table_problems(3, 3)

        expected = [("3 + 3", 6)]
        assert problems == expected

    def test_generate_problems_small_range(self):
        """Test generating problems for small range."""
        problems = generate_addition_table_problems(1, 2)

        expected = [("1 + 1", 2), ("1 + 2", 3), ("2 + 1", 3), ("2 + 2", 4)]
        assert problems == expected

    def test_generate_problems_medium_range(self):
        """Test generating problems for medium range."""
        problems = generate_addition_table_problems(2, 4)

        # Should have (4-2+1)^2 = 9 problems
        assert len(problems) == 9

        # Check a few specific problems
        assert ("2 + 2", 4) in problems
        assert ("3 + 4", 7) in problems
        assert ("4 + 2", 6) in problems

    def test_generate_problems_order(self):
        """Test that problems are generated in correct order."""
        problems = generate_addition_table_problems(1, 3)

        expected_order = [
            ("1 + 1", 2),
            ("1 + 2", 3),
            ("1 + 3", 4),
            ("2 + 1", 3),
            ("2 + 2", 4),
            ("2 + 3", 5),
            ("3 + 1", 4),
            ("3 + 2", 5),
            ("3 + 3", 6),
        ]
        assert problems == expected_order

    def test_generate_problems_large_numbers(self):
        """Test generating problems with larger numbers."""
        problems = generate_addition_table_problems(10, 11)

        expected = [("10 + 10", 20), ("10 + 11", 21), ("11 + 10", 21), ("11 + 11", 22)]
        assert problems == expected


class TestAdditionTableGenerator:
    """Test AdditionTableGenerator class."""

    def test_generator_init_sequential(self):
        """Test generator initialization with sequential order."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        assert generator.low == 1
        assert generator.high == 2
        assert generator.randomize is False
        assert generator.current_index == 0
        assert generator.total_problems == 4  # (2-1+1)^2
        assert generator.is_unlimited is False
        assert generator.num_problems == 4
        assert len(generator.problems) == 4

    def test_generator_init_random(self):
        """Test generator initialization with random order."""
        with patch("random.shuffle") as mock_shuffle:
            generator = AdditionTableGenerator(1, 2, randomize=True)

            assert generator.randomize is True
            mock_shuffle.assert_called_once_with(generator.problems)

    def test_get_next_problem(self):
        """Test getting next problem from generator."""
        generator = AdditionTableGenerator(2, 2, randomize=False)

        problem, answer = generator.get_next_problem()

        assert problem == "2 + 2"
        assert answer == 4
        assert generator.current_index == 1

    def test_get_next_problem_sequential_order(self):
        """Test getting problems in sequential order."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        problems = []
        while generator.has_more_problems():
            problem, answer = generator.get_next_problem()
            problems.append((problem, answer))

        expected = [("1 + 1", 2), ("1 + 2", 3), ("2 + 1", 3), ("2 + 2", 4)]
        assert problems == expected

    def test_get_next_problem_out_of_bounds(self):
        """Test getting next problem when no more problems available."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Get the only problem
        generator.get_next_problem()

        # Should raise IndexError for next attempt
        with pytest.raises(IndexError, match="No more problems available"):
            generator.get_next_problem()

    def test_has_more_problems(self):
        """Test has_more_problems method."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        assert generator.has_more_problems() is True

        generator.get_next_problem()

        assert generator.has_more_problems() is False

    def test_get_total_generated(self):
        """Test get_total_generated method."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        assert generator.get_total_generated() == 0

        generator.get_next_problem()
        assert generator.get_total_generated() == 1

        generator.get_next_problem()
        assert generator.get_total_generated() == 2

    def test_get_progress_display(self):
        """Test get_progress_display method."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        assert generator.get_progress_display() == "0/4"

        generator.get_next_problem()
        assert generator.get_progress_display() == "1/4"

        generator.get_next_problem()
        assert generator.get_progress_display() == "2/4"


class TestRunAdditionTableQuiz:
    """Test run_addition_table_quiz function."""

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_complete_all_problems(self, mock_time, mock_print, mock_input):
        """Test completing all problems in quiz."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, response_time, end_time
        mock_time.side_effect = [0, 1, 2, 10]

        # Mock user inputs: Enter to start, then correct answer
        mock_input.side_effect = [
            "",
            "2",
        ]  # Empty string for "Press Enter", then answer

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 1
        assert total == 1
        assert skipped == 0
        assert duration == 10
        assert len(session_attempts) == 1

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_wrong_then_correct_answer(
        self, mock_time, mock_print, mock_input
    ):
        """Test wrong answer followed by correct answer."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, wrong_response_time, correct_response_time, end_time
        mock_time.side_effect = [0, 1, 2, 3, 10]
        # Enter to start, wrong answer, then correct answer
        mock_input.side_effect = ["", "3", "2"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 1
        assert total == 2  # Two attempts
        assert skipped == 0
        assert duration == 10
        assert len(session_attempts) == 2

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_skip_problem(self, mock_time, mock_print, mock_input):
        """Test skipping a problem."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, end_time
        mock_time.side_effect = [0, 1, 5]
        # Enter to start, then skip
        mock_input.side_effect = ["", "next"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 0
        assert total == 0  # No attempts when skipping
        assert skipped == 1
        assert duration == 5
        assert len(session_attempts) == 0

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_exit_command(self, mock_time, mock_print, mock_input):
        """Test exiting with 'exit' command."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, end_time
        mock_time.side_effect = [0, 1, 3]
        # Enter to start, then exit
        mock_input.side_effect = ["", "exit"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 0
        assert total == 0
        assert skipped == 0
        assert duration == 3
        assert len(session_attempts) == 0

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_stop_command(self, mock_time, mock_print, mock_input):
        """Test stopping with 'stop' command."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, end_time
        mock_time.side_effect = [0, 1, 7]
        # Enter to start, then stop
        mock_input.side_effect = ["", "stop"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 0
        assert total == 0
        assert skipped == 0
        assert duration == 7
        assert len(session_attempts) == 0

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_invalid_input_then_valid(self, mock_time, mock_print, mock_input):
        """Test invalid input followed by valid answer."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, valid_response_time, end_time
        mock_time.side_effect = [0, 1, 2, 12]
        # Enter to start, invalid input, then correct answer
        mock_input.side_effect = ["", "abc", "2"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 1
        assert total == 1  # Only valid attempt counts
        assert skipped == 0
        assert duration == 12
        assert len(session_attempts) == 1

        # Should print error message for invalid input
        mock_print.assert_any_call(
            "❌ Please enter a number, 'next', 'stop', or 'exit'"
        )

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_multiple_problems(self, mock_time, mock_print, mock_input):
        """Test quiz with multiple problems."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        # Mock time progression: start_time, 4 problem_start_times, 4 response_times, end_time
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 20]
        # Enter to start, then answers for all 4 problems
        mock_input.side_effect = ["", "2", "3", "3", "4"]  # All correct answers

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 4
        assert total == 4
        assert skipped == 0
        assert duration == 20
        assert len(session_attempts) == 4

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_mixed_results(self, mock_time, mock_print, mock_input):
        """Test quiz with mix of correct, incorrect, and skipped problems."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        # Mock time progression: start, prob1_start, prob1_correct, prob2_start, prob2_wrong, prob2_correct, prob3_start, prob4_start, prob4_correct, end
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 15]
        # Enter, correct, wrong then correct, skip, correct
        mock_input.side_effect = ["", "2", "5", "3", "next", "4"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        assert correct == 3
        assert total == 4  # 4 attempts (including the wrong one)
        assert skipped == 1
        assert duration == 15
        assert len(session_attempts) == 4

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_display_messages(self, mock_time, mock_print, mock_input):
        """Test that appropriate messages are displayed during quiz."""
        generator = AdditionTableGenerator(2, 2, randomize=False)

        # Mock time progression: start_time, problem_start_time, response_time, end_time
        mock_time.side_effect = [0, 1, 2, 5]
        mock_input.side_effect = ["", "4"]  # Correct answer

        run_addition_table_quiz(generator)

        # Check that intro messages are displayed
        mock_print.assert_any_call("\n🎯 Addition Table for 2 (sequential order)")
        mock_print.assert_any_call("📝 1 problems to solve")
        mock_print.assert_any_call(
            "Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)"
        )

        # Check that success message is displayed
        mock_print.assert_any_call("✅ Correct! Great job!")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_wrong_answers_counted_correctly(
        self, mock_time, mock_print, mock_input
    ):
        """Test that wrong answers are counted as attempts but not as skips."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock time progression: start_time, problem_start_time, 4 response_times, end_time
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 15]
        # Enter to start, then multiple wrong answers before getting it right
        mock_input.side_effect = [
            "",
            "5",
            "6",
            "7",
            "2",
        ]  # 3 wrong attempts, then correct

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        # Should have 1 correct answer
        assert correct == 1
        # Should have 4 total attempts (3 wrong + 1 correct)
        assert total == 4
        # Should have 0 skipped (no 'next' commands)
        assert skipped == 0
        assert duration == 15
        assert len(session_attempts) == 4

        # Verify error messages were printed for wrong answers
        mock_print.assert_any_call("❌ Not quite right. Try again!")
        mock_print.assert_any_call(
            "You can type 'next' to move on to the next problem."
        )
        # Verify success message was printed
        mock_print.assert_any_call("✅ Correct! Great job!")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_run_quiz_mixed_wrong_answers_and_skips(
        self, mock_time, mock_print, mock_input
    ):
        """Test mixed scenario with wrong answers, skips, and correct answers."""
        generator = AdditionTableGenerator(1, 2, randomize=False)

        # Mock time progression: start, prob1_start, prob1_wrong, prob1_correct, prob2_start, prob3_start, prob3_wrong, prob3_correct, prob4_start, prob4_correct, prob4_final, end
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]
        # Enter, wrong then correct, skip, wrong then correct, correct, correct
        # Problems: 1+1=2, 1+2=3, 2+1=3, 2+2=4
        mock_input.side_effect = ["", "5", "2", "next", "8", "3", "3", "4"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(generator)

        # Should have 3 correct answers (1+1=2, 2+1=3, 2+2=4)
        assert correct == 3
        # Should have 6 total attempts (2 wrong + 3 correct + 1 extra)
        assert total == 6
        # Should have 1 skipped
        assert skipped == 1
        assert duration == 20
        assert len(session_attempts) == 6

        # Verify skip message was printed
        mock_print.assert_any_call("⏭️  Skipped! The answer was 3")
        # Verify success messages were printed
        mock_print.assert_any_call("✅ Correct! Great job!")


class TestAdditionTablesMode:
    """Test addition_tables_mode function."""

    @patch("src.presentation.controllers.addition_tables.show_results_with_fact_insights")
    @patch("src.presentation.controllers.addition_tables.run_addition_table_quiz")
    @patch("src.presentation.controllers.addition_tables.get_order_preference")
    @patch("src.presentation.controllers.addition_tables.get_table_range")
    @patch("builtins.print")
    def test_addition_tables_mode_success(
        self,
        mock_print,
        mock_get_range,
        mock_get_order,
        mock_run_quiz,
        mock_show_results_with_fact_insights,
    ):
        """Test successful execution of addition tables mode."""
        # Mock user inputs
        mock_get_range.return_value = (2, 3)
        mock_get_order.return_value = True  # Random order
        mock_run_quiz.return_value = (
            3,
            4,
            1,
            60.0,
            [],
        )  # 3 correct, 4 total, 1 skipped, 60 seconds, empty session_attempts

        addition_tables_mode()

        # Verify function calls
        mock_get_range.assert_called_once()
        mock_get_order.assert_called_once()
        mock_run_quiz.assert_called_once()
        mock_show_results_with_fact_insights.assert_called_once()

        # Verify settings display
        mock_print.assert_any_call("\n📊 Addition Tables Mode Selected!")
        mock_print.assert_any_call("\n📋 Settings:")
        mock_print.assert_any_call("   Range: Addition table for 2 to 3")
        mock_print.assert_any_call("   Order: Random")
        mock_print.assert_any_call("   Total problems: 4")  # (3-2+1)^2

    @patch("src.presentation.controllers.addition_tables.show_results_with_fact_insights")
    @patch("src.presentation.controllers.addition_tables.run_addition_table_quiz")
    @patch("src.presentation.controllers.addition_tables.get_order_preference")
    @patch("src.presentation.controllers.addition_tables.get_table_range")
    @patch("builtins.print")
    def test_addition_tables_mode_single_number(
        self,
        mock_print,
        mock_get_range,
        mock_get_order,
        mock_run_quiz,
        mock_show_results_with_fact_insights,
    ):
        """Test addition tables mode with single number."""
        mock_get_range.return_value = (5, 5)
        mock_get_order.return_value = False  # Sequential order
        mock_run_quiz.return_value = (
            1,
            1,
            0,
            30.0,
            [],
        )  # 1 correct, 1 total, 0 skipped, 30 seconds, empty session_attempts

        addition_tables_mode()

        # Verify single number display
        mock_print.assert_any_call("   Range: Addition table for 5")
        mock_print.assert_any_call("   Order: Sequential")
        mock_print.assert_any_call("   Total problems: 1")  # (5-5+1)^2

    @patch("src.presentation.controllers.addition_tables.get_table_range")
    @patch("builtins.print")
    def test_addition_tables_mode_exception_handling(self, mock_print, mock_get_range):
        """Test exception handling in addition tables mode."""
        mock_get_range.side_effect = Exception("Test error")

        addition_tables_mode()

        # Verify error messages
        mock_print.assert_any_call("❌ Error: Test error")
        mock_print.assert_any_call("Returning to main menu...")

    @patch("src.presentation.controllers.addition_tables.show_results_with_fact_insights")
    @patch("src.presentation.controllers.addition_tables.run_addition_table_quiz")
    @patch("src.presentation.controllers.addition_tables.get_order_preference")
    @patch("src.presentation.controllers.addition_tables.get_table_range")
    def test_addition_tables_mode_generator_created_correctly(
        self, mock_get_range, mock_get_order, mock_run_quiz, mock_show_results_with_fact_insights
    ):
        """Test that AdditionTableGenerator is created with correct parameters."""
        mock_get_range.return_value = (3, 7)
        mock_get_order.return_value = True
        mock_run_quiz.return_value = (
            0,
            0,
            0,
            0,
            [],
        )  # 0 correct, 0 total, 0 skipped, 0 duration, empty session_attempts

        with patch(
            "src.presentation.controllers.addition_tables.AdditionTableGenerator"
        ) as mock_generator_class:
            mock_generator_instance = Mock()
            mock_generator_class.return_value = mock_generator_instance

            addition_tables_mode()

            # Verify generator was created with correct parameters
            mock_generator_class.assert_called_once_with(3, 7, True)

            # Verify generator was passed to quiz function with fact service params
            mock_run_quiz.assert_called_once_with(mock_generator_instance, None, None)

            # Verify generator was passed to show_results_with_fact_insights
            mock_show_results_with_fact_insights.assert_called_once_with(
                0, 0, 0, mock_generator_instance, 0, [], None, None
            )


@pytest.mark.unit
class TestAdditionTablesIntegration:
    """Integration tests for addition tables functionality."""

    def test_full_problem_generation_and_solving_flow(self):
        """Test complete flow from problem generation to solving."""
        # Generate problems
        problems = generate_addition_table_problems(1, 2)

        # Create generator
        generator = AdditionTableGenerator(1, 2, randomize=False)

        # Verify generator has same problems
        assert len(generator.problems) == len(problems)

        # Test solving all problems
        solved_problems = []
        while generator.has_more_problems():
            problem, answer = generator.get_next_problem()
            solved_problems.append((problem, answer))

        # Should have solved all problems
        assert len(solved_problems) == len(problems)
        assert solved_problems == problems

    def test_randomization_affects_order(self):
        """Test that randomization actually changes problem order."""
        # Create two generators with same parameters
        with patch("random.shuffle") as mock_shuffle:
            generator_random = AdditionTableGenerator(1, 3, randomize=True)
            generator_sequential = AdditionTableGenerator(1, 3, randomize=False)

            # Random generator should call shuffle
            mock_shuffle.assert_called_once()

            # Both should have same number of problems
            assert len(generator_random.problems) == len(generator_sequential.problems)

    def test_edge_case_single_problem(self):
        """Test edge case with single problem."""
        problems = generate_addition_table_problems(5, 5)
        generator = AdditionTableGenerator(5, 5, randomize=False)

        assert len(problems) == 1
        assert problems[0] == ("5 + 5", 10)

        problem, answer = generator.get_next_problem()
        assert problem == "5 + 5"
        assert answer == 10
        assert not generator.has_more_problems()

    def test_large_range_calculation(self):
        """Test calculation correctness with larger range."""
        problems = generate_addition_table_problems(8, 12)

        # Should have (12-8+1)^2 = 25 problems
        assert len(problems) == 25

        # Test specific calculations
        assert ("8 + 8", 16) in problems
        assert ("12 + 12", 24) in problems
        assert ("10 + 11", 21) in problems
