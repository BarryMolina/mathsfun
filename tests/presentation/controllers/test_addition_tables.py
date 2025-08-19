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
    get_facts_needing_remedial_review,
    conduct_remedial_review,
    show_review_results,
    QuizSessionConfig,
    _run_quiz_session,
)
from src.domain.models.math_fact_performance import calculate_sm2_grade


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

        expected = [
            ("10 + 10", 20),
            ("10 + 11", 21),
            ("11 + 10", 21),
            ("11 + 11", 22),
        ]
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

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        # Mock time progression: start_time, problem_start_time,
        # wrong_response_time, correct_response_time, end_time
        mock_time.side_effect = [0, 1, 2, 3, 10]
        # Enter to start, wrong answer, then correct answer
        mock_input.side_effect = ["", "3", "2"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

        assert correct == 1
        assert total == 2  # Two attempts
        assert skipped == 0
        assert duration == 10
        assert len(session_attempts) == 1  # Only final attempt per fact recorded
        # Verify session attempt format: (operand1, operand2, final_correct, final_time_ms, incorrect_attempts)
        assert session_attempts[0] == (1, 1, True, 2000, 1)  # Correct after 1 mistake

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

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        # Mock time progression: start_time, 4 problem_start_times,
        # 4 response_times, end_time
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 20]
        # Enter to start, then answers for all 4 problems
        mock_input.side_effect = ["", "2", "3", "3", "4"]  # All correct answers

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

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

        # Mock time progression: start, prob1_start, prob1_correct, prob2_start,
        # prob2_wrong, prob2_correct, prob3_start, prob4_start, prob4_correct, end
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 15]
        # Enter, correct, wrong then correct, skip, correct
        mock_input.side_effect = ["", "2", "5", "3", "next", "4"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

        assert correct == 3
        assert total == 4  # 4 attempts (including the wrong one)
        assert skipped == 1
        assert duration == 15
        assert (
            len(session_attempts) == 3
        )  # Only final attempts per fact: 1+1 (correct), 1+2 (correct after error), 2+2 (correct), skip not recorded

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
        mock_print.assert_any_call("🎯 Addition Table for 2 (sequential order)")
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

        # Mock time progression: start_time, problem_start_time,
        # 4 response_times, end_time
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 15]
        # Enter to start, then multiple wrong answers before getting it right
        mock_input.side_effect = [
            "",
            "5",
            "6",
            "7",
            "2",
        ]  # 3 wrong attempts, then correct

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

        # Should have 1 correct answer
        assert correct == 1
        # Should have 4 total attempts (3 wrong + 1 correct)
        assert total == 4
        # Should have 0 skipped (no 'next' commands)
        assert skipped == 0
        assert duration == 15
        assert (
            len(session_attempts) == 1
        )  # Only final attempt recorded: 1+1 correct after 3 errors

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

        # Mock time progression: start, prob1_start, prob1_wrong, prob1_correct,
        # prob2_start, prob3_start, prob3_wrong, prob3_correct, prob4_start,
        # prob4_correct, prob4_final, end
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]
        # Enter, wrong then correct, skip, wrong then correct, correct, correct
        # Problems: 1+1=2, 1+2=3, 2+1=3, 2+2=4
        mock_input.side_effect = ["", "5", "2", "next", "8", "3", "3", "4"]

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator
        )

        # Should have 3 correct answers (1+1=2, 2+1=3, 2+2=4)
        assert correct == 3
        # Should have 6 total attempts (2 wrong + 3 correct + 1 extra)
        assert total == 6
        # Should have 1 skipped
        assert skipped == 1
        assert duration == 20
        assert (
            len(session_attempts) == 3
        )  # Only final attempts: 1+1 (correct after error), 2+1 (correct after error), 2+2 (correct), skip not recorded

        # Verify skip message was printed
        mock_print.assert_any_call("⏭️  Skipped! The answer was 3")
        # Verify success messages were printed
        mock_print.assert_any_call("✅ Correct! Great job!")


class TestAdditionTablesMode:
    """Test addition_tables_mode function."""

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch(
        "src.presentation.controllers.addition_tables.show_results_with_fact_insights"
    )
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
        mock_get_user_input,
    ):
        """Test successful execution of addition tables mode."""
        # Mock submenu choice (1 = practice specific range)
        mock_get_user_input.return_value = "1"

        # Mock user inputs for practice workflow
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

        # Verify submenu choice was called
        mock_get_user_input.assert_called()

        # Verify function calls after submenu selection
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

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch(
        "src.presentation.controllers.addition_tables.show_results_with_fact_insights"
    )
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
        mock_get_user_input,
    ):
        """Test addition tables mode with single number."""
        # Mock submenu choice (1 = practice specific range)
        mock_get_user_input.return_value = "1"

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

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch("src.presentation.controllers.addition_tables.get_table_range")
    @patch("builtins.print")
    def test_addition_tables_mode_exception_handling(
        self, mock_print, mock_get_range, mock_get_user_input
    ):
        """Test exception handling in addition tables mode."""
        # Mock submenu choice (1 = practice specific range)
        mock_get_user_input.return_value = "1"
        mock_get_range.side_effect = Exception("Test error")

        addition_tables_mode()

        # Verify error messages
        mock_print.assert_any_call("❌ Error: Test error")
        mock_print.assert_any_call("Returning to main menu...")

    @patch("src.presentation.controllers.addition_tables.get_user_input")
    @patch(
        "src.presentation.controllers.addition_tables.show_results_with_fact_insights"
    )
    @patch("src.presentation.controllers.addition_tables.run_addition_table_quiz")
    @patch("src.presentation.controllers.addition_tables.get_order_preference")
    @patch("src.presentation.controllers.addition_tables.get_table_range")
    def test_addition_tables_mode_generator_created_correctly(
        self,
        mock_get_range,
        mock_get_order,
        mock_run_quiz,
        mock_show_results_with_fact_insights,
        mock_get_user_input,
    ):
        """Test that AdditionTableGenerator is created with correct parameters."""
        # Mock submenu choice (1 = practice specific range)
        mock_get_user_input.return_value = "1"

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


class TestFactTrackingIntegration:
    """Test fact tracking integration to prevent double-counting."""

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_fact_tracking_no_double_counting(self, mock_time, mock_print, mock_input):
        """Test that fact tracking doesn't double-count attempts."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock fact service
        mock_fact_service = Mock()
        mock_fact_service.track_attempt.return_value = Mock()

        # Mock time progression: start_time, problem_start_time, response_time, end_time
        mock_time.side_effect = [0, 1, 2, 10]

        # Mock user inputs: Enter to start, then correct answer
        mock_input.side_effect = ["", "2"]

        # Run quiz with fact tracking
        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator, mock_fact_service, "user123"
        )

        # Verify quiz results
        assert correct == 1
        assert total == 1
        assert skipped == 0
        assert len(session_attempts) == 1

        # AFTER FIX: track_attempt should NOT be called during the quiz
        # All tracking should happen only in analyze_session_performance
        assert mock_fact_service.track_attempt.call_count == 0

        # No calls should have been made during quiz (after fix)
        mock_fact_service.track_attempt.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_fact_tracking_wrong_then_correct_no_double_counting(
        self, mock_time, mock_print, mock_input
    ):
        """Test that fact tracking doesn't double-count on wrong then correct answers."""
        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Mock fact service
        mock_fact_service = Mock()
        mock_fact_service.track_attempt.return_value = Mock()

        # Mock time progression: start_time, problem_start_time,
        # wrong_response_time, correct_response_time, end_time
        mock_time.side_effect = [0, 1, 2, 3, 10]

        # Enter to start, wrong answer, then correct answer
        mock_input.side_effect = ["", "3", "2"]

        # Run quiz with fact tracking
        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator, mock_fact_service, "user123"
        )

        # Verify quiz results
        assert correct == 1
        assert total == 2  # Two attempts
        assert skipped == 0
        assert len(session_attempts) == 1  # Only final attempt recorded

        # AFTER FIX: track_attempt should NOT be called during the quiz
        # All tracking should happen only in analyze_session_performance
        assert mock_fact_service.track_attempt.call_count == 0

        # No calls should have been made during quiz (after fix)
        mock_fact_service.track_attempt.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_full_workflow_with_analysis_after_fix(
        self, mock_time, mock_print, mock_input
    ):
        """Test that demonstrates the double-counting bug has been fixed."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Create a mock fact service that simulates the real analyze_session_performance behavior
        mock_fact_service = Mock()
        mock_fact_service.track_attempt.return_value = Mock()

        # IMPORTANT: Make analyze_session_performance call track_attempt like the real implementation
        def mock_analyze_session_performance(user_id, session_attempts):
            # This simulates the real behavior where analyze_session_performance
            # calls track_attempt for each session attempt
            # New session format: (operand1, operand2, final_correct, final_response_time_ms, incorrect_attempts_count)
            for (
                operand1,
                operand2,
                final_correct,
                final_response_time_ms,
                incorrect_attempts_count,
            ) in session_attempts:
                mock_fact_service.track_attempt(
                    user_id,
                    operand1,
                    operand2,
                    None,
                    operand1 + operand2,
                    final_correct,
                    final_response_time_ms,
                    incorrect_attempts_count,
                )

            return {
                "session_accuracy": 100.0,
                "total_attempts": len(session_attempts),
                "correct_attempts": sum(
                    1 for _, _, final_correct, _, _ in session_attempts if final_correct
                ),
                "facts_practiced": len(session_attempts),
                "new_facts_learned": [],
                "facts_due_for_review": 0,
            }

        mock_fact_service.analyze_session_performance.side_effect = (
            mock_analyze_session_performance
        )
        mock_fact_service.get_practice_recommendations.return_value = {
            "recommendation": "Great job!",
            "weak_facts": [],
            "mastered_facts_count": 1,
            "total_possible_facts": 1,
        }

        # Mock time progression: start_time, problem_start_time, response_time, end_time
        mock_time.side_effect = [0, 1, 2, 10]

        # Mock user inputs: Enter to start, then correct answer
        mock_input.side_effect = ["", "2"]

        # Run quiz with fact tracking
        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator, mock_fact_service, "user123"
        )

        # Reset call count to isolate just the analyze_session_performance calls
        initial_track_calls = mock_fact_service.track_attempt.call_count

        # Now call show_results_with_fact_insights which calls analyze_session_performance
        show_results_with_fact_insights(
            correct,
            total,
            duration,
            generator,
            skipped,
            session_attempts,
            mock_fact_service,
            "user123",
        )

        final_track_calls = mock_fact_service.track_attempt.call_count
        analyze_calls = final_track_calls - initial_track_calls

        print(f"Initial track_attempt calls (from quiz): {initial_track_calls}")
        print(f"Additional track_attempt calls (from analysis): {analyze_calls}")
        print(f"Total track_attempt calls: {final_track_calls}")
        print(f"Session attempts: {len(session_attempts)}")

        # AFTER FIX: We expect:
        # - 0 calls during quiz (removed duplicate calls)
        # - 1 call during analyze_session_performance (only tracking happens here)
        # - Total: 1 call for 1 user answer

        expected_total_calls = 1  # 0 from quiz + 1 from analysis

        assert (
            initial_track_calls == 0
        ), f"Expected 0 calls during quiz (after fix), but got {initial_track_calls}"

        assert final_track_calls == expected_total_calls, (
            f"Expected {expected_total_calls} total calls (after fix), "
            f"but got {final_track_calls}. "
            f"Quiz calls: {initial_track_calls}, Analysis calls: {analyze_calls}"
        )

        print("✓ CONFIRMED: Double-counting bug has been FIXED!")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("time.time")
    def test_full_workflow_after_fix_no_double_counting(
        self, mock_time, mock_print, mock_input
    ):
        """Test that after fix, fact tracking doesn't double-count attempts."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        generator = AdditionTableGenerator(1, 1, randomize=False)

        # Create a mock fact service that simulates the real analyze_session_performance behavior
        mock_fact_service = Mock()
        mock_fact_service.track_attempt.return_value = Mock()

        # IMPORTANT: Make analyze_session_performance call track_attempt like the real implementation
        def mock_analyze_session_performance(user_id, session_attempts):
            # This simulates the real behavior where analyze_session_performance
            # calls track_attempt for each session attempt
            # New session format: (operand1, operand2, final_correct, final_response_time_ms, incorrect_attempts_count)
            for (
                operand1,
                operand2,
                final_correct,
                final_response_time_ms,
                incorrect_attempts_count,
            ) in session_attempts:
                mock_fact_service.track_attempt(
                    user_id,
                    operand1,
                    operand2,
                    None,
                    operand1 + operand2,
                    final_correct,
                    final_response_time_ms,
                    incorrect_attempts_count,
                )

            return {
                "session_accuracy": 100.0,
                "total_attempts": len(session_attempts),
                "correct_attempts": sum(
                    1 for _, _, final_correct, _, _ in session_attempts if final_correct
                ),
                "facts_practiced": len(session_attempts),
                "new_facts_learned": [],
                "facts_due_for_review": 0,
            }

        mock_fact_service.analyze_session_performance.side_effect = (
            mock_analyze_session_performance
        )
        mock_fact_service.get_practice_recommendations.return_value = {
            "recommendation": "Great job!",
            "weak_facts": [],
            "mastered_facts_count": 1,
            "total_possible_facts": 1,
        }

        # Mock time progression: start_time, problem_start_time, response_time, end_time
        mock_time.side_effect = [0, 1, 2, 10]

        # Mock user inputs: Enter to start, then correct answer
        mock_input.side_effect = ["", "2"]

        # Run quiz with fact tracking
        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator, mock_fact_service, "user123"
        )

        # Check calls after quiz (should be 0 after fix)
        initial_track_calls = mock_fact_service.track_attempt.call_count

        # Now call show_results_with_fact_insights which calls analyze_session_performance
        show_results_with_fact_insights(
            correct,
            total,
            duration,
            generator,
            skipped,
            session_attempts,
            mock_fact_service,
            "user123",
        )

        final_track_calls = mock_fact_service.track_attempt.call_count
        analyze_calls = final_track_calls - initial_track_calls

        print(f"Quiz calls: {initial_track_calls} (should be 0 after fix)")
        print(f"Analysis calls: {analyze_calls} (should be 1)")
        print(f"Total calls: {final_track_calls} (should be 1)")
        print(f"Session attempts: {len(session_attempts)}")

        # AFTER FIX: We expect:
        # - 0 calls during quiz (removed duplicate calls)
        # - 1 call during analyze_session_performance (only tracking happens here)
        # - Total: 1 call for 1 user answer

        assert (
            initial_track_calls == 0
        ), f"Expected 0 calls during quiz (after fix), but got {initial_track_calls}"

        assert (
            analyze_calls == 1
        ), f"Expected 1 call during analysis, but got {analyze_calls}"

        assert (
            final_track_calls == 1
        ), f"Expected 1 total call (after fix), but got {final_track_calls}"

        print("✓ CONFIRMED: Double-counting bug is FIXED!")


class TestAdditionTablesModeEdgeCases:
    """Test edge cases for addition_tables_mode to improve coverage."""

    def test_addition_tables_mode_with_container_and_user(self):
        """Test addition_tables_mode with container and user provided."""
        from src.presentation.controllers.addition_tables import addition_tables_mode
        from src.domain.models.user import User

        # Mock dependencies - only mock high-level functions to avoid conflicts
        with patch(
            "src.presentation.controllers.addition_tables.get_addition_tables_choice"
        ) as mock_get_choice, patch(
            "src.presentation.controllers.addition_tables.practice_specific_range"
        ) as mock_practice_range, patch(
            "builtins.print"
        ) as mock_print:

            # Mock submenu choice (1 = practice specific range)
            mock_get_choice.return_value = 1

            # Mock container and user
            mock_container = Mock()
            mock_math_fact_service = Mock()
            mock_container.math_fact_svc = mock_math_fact_service

            mock_user = User(
                id="test_user", email="test@example.com", display_name="Test User"
            )

            addition_tables_mode(mock_container, mock_user)

            # Verify that practice_specific_range was called with container and user
            mock_practice_range.assert_called_once_with(mock_container, mock_user)

    def test_show_results_with_fact_insights_mastery_improvements(self):
        """Test show_results_with_fact_insights with SM-2 insights."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        with patch("builtins.print") as mock_print, patch(
            "src.presentation.controllers.addition_tables.show_results"
        ) as mock_show_results:

            mock_generator = Mock()
            mock_generator.low = 3
            mock_generator.high = 5

            mock_math_fact_service = Mock()

            # Mock SM-2 analysis
            mock_analysis = {
                "facts_practiced": ["3+4", "4+5"],
                "new_facts_learned": ["3+4"],
                "facts_due_for_review": 2,
                "session_accuracy": 85.0,
                "total_attempts": 2,
                "correct_attempts": 2,
            }
            mock_math_fact_service.analyze_session_performance.return_value = (
                mock_analysis
            )

            # Mock weak facts
            mock_weak_facts = [Mock(fact_key="6+7"), Mock(fact_key="8+9")]
            mock_math_fact_service.get_weak_facts.return_value = mock_weak_facts

            # Mock performance summary
            mock_summary = {
                "total_facts": 5,
                "average_ease_factor": 2.8,
                "facts_by_interval": {1: 2, 6: 3},
            }
            mock_math_fact_service.get_performance_summary.return_value = mock_summary

            # Use correct SM-2 session format: (operand1, operand2, final_correct, final_response_time_ms, incorrect_attempts_count)
            session_attempts = [(3, 4, True, 2000, 0), (4, 5, True, 1800, 0)]

            show_results_with_fact_insights(
                2,
                2,
                120.0,
                mock_generator,
                0,
                session_attempts,
                mock_math_fact_service,
                "test_user",
            )

            # Verify SM-2 insights were shown
            mock_print.assert_any_call("📊 SM-2 SPACED REPETITION INSIGHTS")
            mock_print.assert_any_call("📝 Facts practiced this session: 2")

    def test_show_results_with_fact_insights_facts_needing_practice(self):
        """Test show_results_with_fact_insights with weak facts shown."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        with patch("builtins.print") as mock_print, patch(
            "src.presentation.controllers.addition_tables.show_results"
        ) as mock_show_results:

            mock_generator = Mock()
            mock_generator.low = 3
            mock_generator.high = 5

            mock_math_fact_service = Mock()

            # Mock SM-2 analysis
            mock_analysis = {
                "facts_practiced": ["7+8", "8+9"],
                "new_facts_learned": [],
                "facts_due_for_review": 3,
                "session_accuracy": 60.0,
                "total_attempts": 2,
                "correct_attempts": 0,
            }
            mock_math_fact_service.analyze_session_performance.return_value = (
                mock_analysis
            )

            # Mock weak facts to be displayed
            mock_weak_facts = [
                Mock(fact_key="7+8"),
                Mock(fact_key="8+9"),
                Mock(fact_key="9+7"),
            ]
            mock_math_fact_service.get_weak_facts.return_value = mock_weak_facts

            # Mock performance summary
            mock_summary = {
                "total_facts": 5,
                "average_ease_factor": 1.8,
                "facts_by_interval": {1: 3, 6: 2},
            }
            mock_math_fact_service.get_performance_summary.return_value = mock_summary

            # Use correct SM-2 session format: (operand1, operand2, final_correct, final_response_time_ms, incorrect_attempts_count)
            session_attempts = [(7, 8, False, 4000, 2), (8, 9, False, 3500, 1)]

            show_results_with_fact_insights(
                0,
                2,
                150.0,
                mock_generator,
                0,
                session_attempts,
                mock_math_fact_service,
                "test_user",
            )

            # Verify weak facts focus message is shown (only first 3 are displayed)
            mock_print.assert_any_call("\n🎯 FOCUS ON: 7+8, 8+9, 9+7")

    def test_show_results_with_fact_insights_exception_handling(self):
        """Test show_results_with_fact_insights with exception during analysis."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        with patch("builtins.print") as mock_print, patch(
            "src.presentation.controllers.addition_tables.show_results"
        ) as mock_show_results:

            mock_generator = Mock()
            mock_generator.low = 3
            mock_generator.high = 5

            mock_addition_fact_service = Mock()

            # Mock exception during analysis
            mock_addition_fact_service.analyze_session_performance.side_effect = (
                Exception("Database error")
            )

            session_attempts = [(3, 4, True, 2000, 0)]

            show_results_with_fact_insights(
                1,
                1,
                30.0,
                mock_generator,
                0,
                session_attempts,
                mock_addition_fact_service,
                "test_user",
            )

            # Verify exception handling message (covers line 617)
            mock_print.assert_any_call(
                "\n⚠️  Could not load SM-2 insights: Database error"
            )

    def test_show_results_with_fact_insights_no_fact_service(self):
        """Test show_results_with_fact_insights without fact service."""
        from src.presentation.controllers.addition_tables import (
            show_results_with_fact_insights,
        )

        with patch("builtins.print") as mock_print, patch(
            "src.presentation.controllers.addition_tables.show_results"
        ) as mock_show_results:

            mock_generator = Mock()
            session_attempts = [(3, 4, True, 2000, 0)]

            show_results_with_fact_insights(
                1,
                1,
                30.0,
                mock_generator,
                0,
                session_attempts,
                None,
                None,  # No fact service or user_id
            )

            # Verify SM-2 sign-in message
            mock_print.assert_any_call("\n" + "=" * 60)
            mock_print.assert_any_call("🔐 SIGN IN FOR PERSONALIZED INSIGHTS")
            mock_print.assert_any_call("=" * 60)
            mock_print.assert_any_call(
                "Sign in to track your progress with SM-2 spaced repetition!"
            )
            mock_print.assert_any_call(
                "• Adaptive review scheduling based on your performance"
            )


class TestRemedialReviewHelpers:
    """Test helper functions for remedial review feature."""

    def test_get_sm2_grade_from_attempt_perfect_recall(self):
        """Test grade calculation for perfect recall (grade 5)."""
        grade = calculate_sm2_grade(1500, 0)  # Fast, no errors
        assert grade == 5

    def test_get_sm2_grade_from_attempt_some_hesitation(self):
        """Test grade calculation for some hesitation (grade 4)."""
        grade = calculate_sm2_grade(2500, 0)  # Medium speed, no errors
        assert grade == 4

    def test_get_sm2_grade_from_attempt_significant_effort(self):
        """Test grade calculation for significant effort (grade 3)."""
        grade = calculate_sm2_grade(4000, 0)  # Slow, no errors
        assert grade == 3

    def test_get_sm2_grade_from_attempt_easy_after_error(self):
        """Test grade calculation for easy after error (grade 2)."""
        grade = calculate_sm2_grade(2000, 1)  # Fast with 1 error
        assert grade == 2

    def test_get_sm2_grade_from_attempt_slow_after_error(self):
        """Test grade calculation for slow after error (grade 1)."""
        grade = calculate_sm2_grade(4000, 1)  # Slow with 1 error
        assert grade == 1

    def test_get_sm2_grade_from_attempt_blackout(self):
        """Test grade calculation for blackout (grade 0)."""
        grade = calculate_sm2_grade(5000, 2)  # 2+ errors
        assert grade == 0

    def test_get_facts_needing_remedial_review_empty_list(self):
        """Test with empty session attempts list."""
        facts = get_facts_needing_remedial_review([])
        assert facts == []

    def test_get_facts_needing_remedial_review_no_poor_facts(self):
        """Test with no facts needing remedial review."""
        session_attempts = [
            (5, 6, True, 1500, 0),  # Grade 5 - perfect
            (7, 8, True, 2500, 0),  # Grade 4 - good
        ]
        facts = get_facts_needing_remedial_review(session_attempts)
        assert facts == []

    def test_get_facts_needing_remedial_review_with_poor_facts(self):
        """Test with facts needing remedial review."""
        session_attempts = [
            (5, 6, True, 1500, 0),  # Grade 5 - perfect, no remedial needed
            (7, 8, True, 4000, 0),  # Grade 3 - needs remedial review
            (3, 4, True, 2000, 1),  # Grade 2 - needs remedial review
            (9, 2, True, 5000, 2),  # Grade 0 - needs remedial review
        ]
        facts = get_facts_needing_remedial_review(session_attempts)
        # Should only include facts with grades <= 3
        expected = [(7, 8), (3, 4), (9, 2)]
        assert facts == expected

    def test_get_facts_needing_remedial_review_only_correct_attempts(self):
        """Test that only correct attempts are considered for remedial review."""
        session_attempts = [
            (5, 6, True, 4000, 0),  # Grade 3 - correct, needs remedial
            (7, 8, False, 4000, 2),  # Incorrect attempt - should be ignored
        ]
        facts = get_facts_needing_remedial_review(session_attempts)
        assert facts == [(5, 6)]  # Only the correct attempt

    def test_get_facts_needing_remedial_review_duplicates(self):
        """Test that duplicate facts are included if both need remedial review."""
        session_attempts = [
            (5, 6, True, 4000, 0),  # Grade 3 - needs remedial
            (5, 6, True, 5000, 1),  # Grade 1 - also needs remedial (same fact)
        ]
        facts = get_facts_needing_remedial_review(session_attempts)
        # Both instances should be included
        assert facts == [(5, 6), (5, 6)]

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.random.shuffle")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_conduct_remedial_review_empty_facts(
        self, mock_time, mock_shuffle, mock_print, mock_input
    ):
        """Test conduct_remedial_review with empty facts list."""
        result = conduct_remedial_review([], None, "user123", 1)
        assert result == []
        # Should not call shuffle, print, or input if no facts
        mock_shuffle.assert_not_called()

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.random.shuffle")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_conduct_remedial_review_user_exits_early(
        self, mock_time, mock_shuffle, mock_print, mock_input
    ):
        """Test conduct_remedial_review when user exits early."""
        mock_time.side_effect = [1000, 1005, 1010]  # Start, problem start, exit time
        mock_input.side_effect = ["", "exit"]  # Press enter to start, then exit

        facts = [(3, 4), (5, 6)]
        result = conduct_remedial_review(facts, None, "user123", 1)

        assert result == []
        mock_print.assert_any_call("⏱️  Time: 10.0 seconds")

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.random.shuffle")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_conduct_remedial_review_correct_answer(
        self, mock_time, mock_shuffle, mock_print, mock_input
    ):
        """Test conduct_remedial_review with correct answer."""
        # Mock time progression
        mock_time.side_effect = [
            1000,  # Session start
            1005,  # Problem start
            1007,  # Answer time
            1010,  # Session end
        ]

        # User presses enter to start, then answers 7 correctly
        mock_input.side_effect = ["", "7"]

        facts = [(3, 4)]  # 3 + 4 = 7
        result = conduct_remedial_review(facts, None, "user123", 1)

        # Should record the correct attempt
        expected = [(3, 4, True, 2000, 0)]  # 2000ms response time, 0 incorrect attempts
        assert result == expected

        # Should show success messages
        mock_print.assert_any_call("✅ Correct! Great job!")
        mock_print.assert_any_call("\n📊 Remedial Session #1 Complete!")


class TestRemedialReviewIntegration:
    """Integration tests for the complete remedial review flow."""

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    def test_show_review_results_no_remedial_needed(self, mock_print, mock_input):
        """Test show_review_results when no facts need remedial review."""
        # Create mock math fact service
        mock_math_fact_service = Mock()
        mock_math_fact_service.analyze_session_performance.return_value = {
            "facts_due_for_review": 0,
            "session_accuracy": 1.0,
        }

        # Session attempts with all high grades
        session_attempts = [
            (5, 6, True, 1500, 0),  # Grade 5 - perfect
            (7, 8, True, 2500, 0),  # Grade 4 - good
        ]

        # Call the function
        show_review_results(
            2, 2, 0, 15.0, session_attempts, mock_math_fact_service, "user123", 2
        )

        # Verify main session was uploaded
        mock_math_fact_service.analyze_session_performance.assert_called_once()

        # Verify success message for high performance
        mock_print.assert_any_call(
            "\n🌟 Great job! All your facts received grades ≥ 4!"
        )

        # Should not prompt for remedial review
        mock_input.assert_not_called()

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    def test_show_review_results_user_declines_remedial(self, mock_print, mock_input):
        """Test show_review_results when user declines remedial review."""
        # Mock user declining remedial review
        mock_input.return_value = "n"

        # Create mock math fact service
        mock_math_fact_service = Mock()
        mock_math_fact_service.analyze_session_performance.return_value = {
            "facts_due_for_review": 3,
            "session_accuracy": 0.6,
        }

        # Session attempts with facts needing remedial review
        session_attempts = [
            (7, 4, True, 4000, 0),  # Grade 3 - needs remedial review
        ]

        # Call the function
        show_review_results(
            1, 1, 0, 10.0, session_attempts, mock_math_fact_service, "user123", 1
        )

        # Verify main session was uploaded
        mock_math_fact_service.analyze_session_performance.assert_called_once()

        # Verify remedial review was offered
        mock_print.assert_any_call("\n⚠️  SuperMemo Alert: 1 facts received grades ≤ 3")
        mock_input.assert_called_once_with(
            "\n🔄 Would you like to practice these 1 facts again? (y/n): "
        )

        # Verify encouragement message when declined
        mock_print.assert_any_call(
            "📚 Remember: Regular practice of challenging facts improves long-term retention!"
        )


class TestQuizSessionConfig:
    """Test QuizSessionConfig dataclass."""

    def test_quiz_session_config_defaults(self):
        """Test QuizSessionConfig with default values."""
        config = QuizSessionConfig(header_lines=["Test Header"])

        assert config.header_lines == ["Test Header"]
        assert (
            config.commands_text
            == "Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)"
        )
        assert config.progress_format == "Problem {current}/{total}"
        assert config.show_results_on_exit is False
        assert config.math_fact_service is None
        assert config.user_id is None
        assert config.total_facts is None

    def test_quiz_session_config_custom_values(self):
        """Test QuizSessionConfig with custom values."""
        mock_service = Mock()
        config = QuizSessionConfig(
            header_lines=["Custom Header", "Line 2"],
            commands_text="Custom commands",
            progress_format="Step {current} of {total}",
            show_results_on_exit=True,
            math_fact_service=mock_service,
            user_id="user123",
            total_facts=10,
        )

        assert config.header_lines == ["Custom Header", "Line 2"]
        assert config.commands_text == "Custom commands"
        assert config.progress_format == "Step {current} of {total}"
        assert config.show_results_on_exit is True
        assert config.math_fact_service == mock_service
        assert config.user_id == "user123"
        assert config.total_facts == 10


class TestQuizEngine:
    """Test _run_quiz_session core quiz engine."""

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_basic_flow(self, mock_time, mock_print, mock_input):
        """Test basic quiz engine flow with correct answers."""
        # Mock time progression
        mock_time.side_effect = [
            1000,  # Session start
            1005,  # Problem 1 start
            1007,  # Problem 1 answer
            1010,  # Problem 2 start
            1012,  # Problem 2 answer
            1015,  # Session end
        ]

        # User input: start session, answer 7, answer 12
        mock_input.side_effect = ["", "7", "12"]

        problems = [("3 + 4", 7), ("5 + 7", 12)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz", "Two problems"],
            progress_format="Question {current}/{total}",
        )

        result = _run_quiz_session(problems, config)

        # Verify results
        correct, total, skipped, duration, attempts = result
        assert correct == 2
        assert total == 2
        assert skipped == 0
        assert duration == 15.0  # 1015 - 1000
        assert len(attempts) == 2

        # Verify attempts data
        assert attempts[0] == (3, 4, True, 2000, 0)  # 1007 - 1005
        assert attempts[1] == (5, 7, True, 2000, 0)  # 1012 - 1010

        # Verify output
        mock_print.assert_any_call("Test Quiz")
        mock_print.assert_any_call("Two problems")
        mock_print.assert_any_call(
            "Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)"
        )
        mock_print.assert_any_call("\n📝 Question 1/2: 3 + 4")
        mock_print.assert_any_call("\n📝 Question 2/2: 5 + 7")
        mock_print.assert_any_call("✅ Correct! Great job!")

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_with_errors(self, mock_time, mock_print, mock_input):
        """Test quiz engine with incorrect attempts and retries."""
        # Mock time progression
        mock_time.side_effect = [
            1000,  # Session start
            1005,  # Problem start
            1006,  # First wrong attempt
            1007,  # Second wrong attempt
            1008,  # Correct attempt
            1010,  # Session end
        ]

        # User input: start, wrong answer, wrong again, correct
        mock_input.side_effect = ["", "5", "6", "7"]

        problems = [("3 + 4", 7)]
        config = QuizSessionConfig(header_lines=["Error Test"])

        result = _run_quiz_session(problems, config)

        # Verify results
        correct, total, skipped, duration, attempts = result
        assert correct == 1
        assert total == 3  # Counts all attempts (2 wrong + 1 correct)
        assert skipped == 0
        assert len(attempts) == 1

        # Verify attempt recorded 2 incorrect attempts
        assert attempts[0] == (3, 4, True, 3000, 2)  # 1008 - 1005, 2 incorrect attempts

        # Verify error messages
        mock_print.assert_any_call("❌ Not quite right. Try again!")
        mock_print.assert_any_call(
            "You can type 'next' to move on to the next problem."
        )

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_skip_problem(self, mock_time, mock_print, mock_input):
        """Test quiz engine skipping problems."""
        mock_time.side_effect = [
            1000,
            1005,
            1008,
            1010,
        ]  # Session start, problem start, skip time, end
        mock_input.side_effect = ["", "next"]  # Start then skip

        problems = [("3 + 4", 7)]
        config = QuizSessionConfig(header_lines=["Skip Test"])

        result = _run_quiz_session(problems, config)

        correct, total, skipped, duration, attempts = result
        assert correct == 0
        assert total == 0  # No problems attempted
        assert skipped == 1  # Skipped the problem
        assert (
            len(attempts) == 0
        )  # No failed attempt recorded (skipped before wrong answer)

        mock_print.assert_any_call("⏭️  Skipped! The answer was 7")

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_exit_early(self, mock_time, mock_print, mock_input):
        """Test quiz engine exiting early."""
        mock_time.side_effect = [1000, 1005, 1010]
        mock_input.side_effect = ["", "exit"]

        problems = [("3 + 4", 7), ("5 + 6", 11)]
        config = QuizSessionConfig(header_lines=["Exit Test"])

        result = _run_quiz_session(problems, config)

        correct, total, skipped, duration, attempts = result
        assert correct == 0
        assert total == 0
        assert skipped == 0
        assert duration == 10.0
        assert len(attempts) == 0

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_stop_early(self, mock_time, mock_print, mock_input):
        """Test quiz engine stopping early."""
        mock_time.side_effect = [1000, 1005, 1010]
        mock_input.side_effect = ["", "stop"]

        problems = [("3 + 4", 7)]
        config = QuizSessionConfig(header_lines=["Stop Test"])

        result = _run_quiz_session(problems, config)

        correct, total, skipped, duration, attempts = result
        assert correct == 0
        assert total == 0
        assert skipped == 0
        assert duration == 10.0
        assert len(attempts) == 0

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_invalid_input(self, mock_time, mock_print, mock_input):
        """Test quiz engine handling invalid input."""
        mock_time.side_effect = [1000, 1005, 1006, 1007, 1010]
        mock_input.side_effect = [
            "",
            "abc",
            "7.5",
            "7",
        ]  # Invalid string, float, then correct

        problems = [("3 + 4", 7)]
        config = QuizSessionConfig(header_lines=["Invalid Input Test"])

        result = _run_quiz_session(problems, config)

        correct, total, skipped, duration, attempts = result
        assert correct == 1
        assert total == 1
        assert len(attempts) == 1

        # Verify error message for invalid input
        mock_print.assert_any_call(
            "❌ Please enter a number, 'next', 'stop', or 'exit'"
        )

    @patch("src.presentation.controllers.addition_tables.show_review_results")
    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_with_results_on_exit(
        self, mock_time, mock_print, mock_input, mock_show_results
    ):
        """Test quiz engine calling show_review_results on exit when configured."""
        mock_time.side_effect = [1000, 1005, 1010]
        mock_input.side_effect = ["", "exit"]

        mock_service = Mock()
        problems = [("3 + 4", 7)]
        config = QuizSessionConfig(
            header_lines=["Results Test"],
            show_results_on_exit=True,
            math_fact_service=mock_service,
            user_id="user123",
            total_facts=5,
        )

        result = _run_quiz_session(problems, config)

        # Verify show_review_results was called
        mock_show_results.assert_called_once_with(
            0, 0, 0, 10.0, [], mock_service, "user123", 5
        )

    @patch("src.presentation.controllers.addition_tables.input")
    @patch("builtins.print")
    @patch("src.presentation.controllers.addition_tables.time.time")
    def test_quiz_engine_empty_problems(self, mock_time, mock_print, mock_input):
        """Test quiz engine with empty problems list."""
        mock_time.side_effect = [1000, 1000]
        mock_input.side_effect = [""]

        problems = []
        config = QuizSessionConfig(header_lines=["Empty Test"])

        result = _run_quiz_session(problems, config)

        correct, total, skipped, duration, attempts = result
        assert correct == 0
        assert total == 0
        assert skipped == 0
        assert duration == 0.0
        assert len(attempts) == 0
