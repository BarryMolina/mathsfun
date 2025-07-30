#!/usr/bin/env python3
"""Tests for addition logic and problem generation."""

import pytest
from hypothesis import given, strategies as st
from src.presentation.controllers.addition import (
    generate_single_digit_numbers,
    generate_two_digit_no_carrying,
    generate_two_digit_with_carrying,
    generate_three_digit_no_carrying,
    generate_three_digit_with_carrying,
    generate_problem_by_difficulty,
    ProblemGenerator,
    DIFFICULTY_DESCRIPTIONS,
)


class TestProblemGeneration:
    """Test individual problem generation functions."""

    def test_generate_single_digit_numbers(self):
        """Test single digit number generation."""
        for _ in range(100):  # Test multiple times due to randomness
            num1, num2 = generate_single_digit_numbers()
            assert 0 <= num1 <= 9
            assert 0 <= num2 <= 9

    def test_generate_two_digit_no_carrying(self):
        """Test two digit number generation without carrying."""
        for _ in range(100):
            num1, num2 = generate_two_digit_no_carrying()

            # Check range
            assert 10 <= num1 <= 99
            assert 10 <= num2 <= 99

            # Check no carrying required
            ones1, tens1 = num1 % 10, num1 // 10
            ones2, tens2 = num2 % 10, num2 // 10

            assert ones1 + ones2 <= 9, f"Ones place carrying: {num1} + {num2}"
            assert tens1 + tens2 <= 9, f"Tens place carrying: {num1} + {num2}"

    def test_generate_two_digit_with_carrying(self):
        """Test two digit number generation with carrying required."""
        for _ in range(100):
            num1, num2 = generate_two_digit_with_carrying()

            # Check range
            assert 10 <= num1 <= 99
            assert 10 <= num2 <= 99

            # Check carrying is required (ones place)
            ones1, ones2 = num1 % 10, num2 % 10
            assert ones1 + ones2 > 9, f"No carrying required: {num1} + {num2}"

    def test_generate_three_digit_no_carrying(self):
        """Test three digit number generation without carrying."""
        for _ in range(100):
            num1, num2 = generate_three_digit_no_carrying()

            # Check range
            assert 100 <= num1 <= 999
            assert 100 <= num2 <= 999

            # Check no carrying required in any position
            ones1, tens1, hundreds1 = num1 % 10, (num1 // 10) % 10, num1 // 100
            ones2, tens2, hundreds2 = num2 % 10, (num2 // 10) % 10, num2 // 100

            assert ones1 + ones2 <= 9, f"Ones place carrying: {num1} + {num2}"
            assert tens1 + tens2 <= 9, f"Tens place carrying: {num1} + {num2}"
            assert (
                hundreds1 + hundreds2 <= 9
            ), f"Hundreds place carrying: {num1} + {num2}"

    def test_generate_three_digit_with_carrying(self):
        """Test three digit number generation with carrying required."""
        for _ in range(100):
            num1, num2 = generate_three_digit_with_carrying()

            # Check range
            assert 100 <= num1 <= 999
            assert 100 <= num2 <= 999

            # Check carrying is required (at least in ones place)
            ones1, ones2 = num1 % 10, num2 % 10
            assert ones1 + ones2 > 9, f"No carrying required: {num1} + {num2}"


class TestGenerateProblemByDifficulty:
    """Test the generate_problem_by_difficulty function."""

    @pytest.mark.parametrize("difficulty", [1, 2, 3, 4, 5])
    def test_valid_difficulties(self, difficulty):
        """Test problem generation for all valid difficulty levels."""
        problem, answer = generate_problem_by_difficulty(difficulty)

        # Check problem format
        assert " + " in problem
        parts = problem.split(" + ")
        assert len(parts) == 2

        num1, num2 = int(parts[0]), int(parts[1])
        assert answer == num1 + num2

        # Check difficulty constraints
        if difficulty == 1:
            assert 0 <= num1 <= 9 and 0 <= num2 <= 9
        elif difficulty in [2, 3]:
            assert 10 <= num1 <= 99 and 10 <= num2 <= 99
        elif difficulty in [4, 5]:
            assert 100 <= num1 <= 999 and 100 <= num2 <= 999

    def test_invalid_difficulty(self):
        """Test that invalid difficulty levels raise ValueError."""
        with pytest.raises(ValueError, match="Invalid difficulty level"):
            generate_problem_by_difficulty(0)

        with pytest.raises(ValueError, match="Invalid difficulty level"):
            generate_problem_by_difficulty(6)


class TestProblemGenerator:
    """Test the ProblemGenerator class."""

    def test_init_limited(self):
        """Test initialization with limited problems."""
        generator = ProblemGenerator(1, 3, 10)

        assert generator.low_difficulty == 1
        assert generator.high_difficulty == 3
        assert generator.difficulty_range == [1, 2, 3]
        assert generator.num_problems == 10
        assert generator.problems_generated == 0
        assert not generator.is_unlimited

    def test_init_unlimited(self):
        """Test initialization with unlimited problems."""
        generator = ProblemGenerator(2, 5, 0)

        assert generator.low_difficulty == 2
        assert generator.high_difficulty == 5
        assert generator.difficulty_range == [2, 3, 4, 5]
        assert generator.num_problems == 0
        assert generator.problems_generated == 0
        assert generator.is_unlimited

    def test_get_next_problem(self):
        """Test problem generation."""
        generator = ProblemGenerator(1, 2, 5)

        problem, answer = generator.get_next_problem()

        # Check problem format
        assert " + " in problem
        parts = problem.split(" + ")
        num1, num2 = int(parts[0]), int(parts[1])
        assert answer == num1 + num2

        # Check counter incremented
        assert generator.problems_generated == 1

    def test_has_more_problems_limited(self):
        """Test has_more_problems for limited generator."""
        generator = ProblemGenerator(1, 1, 2)

        assert generator.has_more_problems()
        generator.get_next_problem()
        assert generator.has_more_problems()
        generator.get_next_problem()
        assert not generator.has_more_problems()

    def test_has_more_problems_unlimited(self):
        """Test has_more_problems for unlimited generator."""
        generator = ProblemGenerator(1, 1, 0)

        for _ in range(100):  # Test many times
            assert generator.has_more_problems()
            generator.get_next_problem()

    def test_get_progress_display_limited(self):
        """Test progress display for limited generator."""
        generator = ProblemGenerator(1, 1, 5)

        assert generator.get_progress_display() == "0/5"
        generator.get_next_problem()
        assert generator.get_progress_display() == "1/5"

    def test_get_progress_display_unlimited(self):
        """Test progress display for unlimited generator."""
        generator = ProblemGenerator(1, 1, 0)

        assert generator.get_progress_display() == "#0"
        generator.get_next_problem()
        assert generator.get_progress_display() == "#1"


class TestConstants:
    """Test module constants."""

    def test_difficulty_descriptions(self):
        """Test that all difficulty levels have descriptions."""
        expected_levels = {1, 2, 3, 4, 5}
        assert set(DIFFICULTY_DESCRIPTIONS.keys()) == expected_levels

        for level, description in DIFFICULTY_DESCRIPTIONS.items():
            assert isinstance(description, str)
            assert len(description) > 0


# Property-based tests using Hypothesis
class TestPropertyBased:
    """Property-based tests for mathematical correctness."""

    @given(st.integers(min_value=1, max_value=5))
    def test_problem_generation_always_valid(self, difficulty):
        """Property: Generated problems should always be mathematically correct."""
        problem, answer = generate_problem_by_difficulty(difficulty)

        # Parse the problem
        parts = problem.split(" + ")
        num1, num2 = int(parts[0]), int(parts[1])

        # Verify mathematical correctness
        assert answer == num1 + num2

        # Verify positive numbers
        assert num1 >= 0
        assert num2 >= 0

    @given(
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=100),
    )
    def test_generator_produces_valid_problems(self, low_diff, high_diff, num_problems):
        """Property: Generator should always produce valid problems within difficulty range."""
        if low_diff > high_diff:
            low_diff, high_diff = high_diff, low_diff

        generator = ProblemGenerator(low_diff, high_diff, num_problems)

        for _ in range(min(10, num_problems)):  # Test up to 10 problems
            if not generator.has_more_problems():
                break

            problem, answer = generator.get_next_problem()

            # Parse and verify
            parts = problem.split(" + ")
            num1, num2 = int(parts[0]), int(parts[1])
            assert answer == num1 + num2


class TestGetDifficultyRangeInputValidation:
    """Test input validation in get_difficulty_range function."""

    def test_invalid_low_difficulty_input(self, mocker, capsys):
        """Test invalid input for low difficulty followed by valid input."""
        from src.presentation.controllers.addition import get_difficulty_range

        # Mock input to provide invalid input first, then valid
        mock_input = mocker.patch("builtins.input", side_effect=["abc", "2", "4"])

        low, high = get_difficulty_range()

        assert low == 2
        assert high == 4
        assert mock_input.call_count == 3

        # Check that error message was printed
        captured = capsys.readouterr()
        assert "❌ Please enter a valid number" in captured.out

    def test_high_less_than_low_difficulty(self, mocker, capsys):
        """Test when high difficulty is less than low difficulty."""
        from src.presentation.controllers.addition import get_difficulty_range

        # Mock input: valid low, then high < low, then valid high
        mock_input = mocker.patch("builtins.input", side_effect=["3", "1", "5"])

        low, high = get_difficulty_range()

        assert low == 3
        assert high == 5
        assert mock_input.call_count == 3

        # Check that error message was printed
        captured = capsys.readouterr()
        assert "❌ High difficulty must be >= low difficulty" in captured.out

    def test_invalid_high_difficulty_input(self, mocker, capsys):
        """Test invalid input for high difficulty followed by valid input."""
        from src.presentation.controllers.addition import get_difficulty_range

        # Mock input: valid low, invalid high, then valid high
        mock_input = mocker.patch("builtins.input", side_effect=["2", "xyz", "4"])

        low, high = get_difficulty_range()

        assert low == 2
        assert high == 4
        assert mock_input.call_count == 3

        # Check that error message was printed
        captured = capsys.readouterr()
        assert "❌ Please enter a valid number" in captured.out


class TestRunAdditionQuizEdgeCases:
    """Test edge cases in run_addition_quiz function."""

    def test_unlimited_mode_start_message(self, mocker, capsys):
        """Test that unlimited mode shows correct start message."""
        from src.presentation.controllers.addition import (
            run_addition_quiz,
            ProblemGenerator,
        )

        # Create unlimited generator
        generator = ProblemGenerator(1, 2, 0)  # 0 means unlimited

        # Mock dependencies
        mock_prompt = mocker.patch(
            "src.presentation.controllers.addition.prompt_start_session"
        )
        mock_input = mocker.patch("builtins.input", return_value="exit")
        mocker.patch.object(generator, "get_next_problem", return_value=("1 + 1", 2))

        run_addition_quiz(generator)

        captured = capsys.readouterr()
        assert (
            "🎯 Timer started! Solve problems until you're ready to stop."
            in captured.out
        )

    def test_quiz_invalid_input_handling(self, mocker, capsys):
        """Test handling of invalid input during quiz."""
        from src.presentation.controllers.addition import (
            run_addition_quiz,
            ProblemGenerator,
        )

        generator = ProblemGenerator(1, 1, 2)

        # Mock dependencies
        mock_prompt = mocker.patch(
            "src.presentation.controllers.addition.prompt_start_session"
        )
        # Provide invalid input, then valid answer, then second valid answer
        mock_input = mocker.patch("builtins.input", side_effect=["invalid", "2", "4"])
        mocker.patch.object(
            generator, "get_next_problem", side_effect=[("1 + 1", 2), ("2 + 2", 4)]
        )
        mocker.patch.object(
            generator, "has_more_problems", side_effect=[True, True, False]
        )

        correct, total, duration = run_addition_quiz(generator)

        assert correct == 2
        assert total == 2

        # Check that error message was printed
        captured = capsys.readouterr()
        assert "❌ Please enter a number, 'next', 'stop', or 'exit'" in captured.out


class TestAdditionModeQuizSession:
    """Test addition mode with quiz session management."""

    def test_run_quiz_with_container_and_user_id(self):
        """Test run_quiz with container and user_id for session management."""
        from src.presentation.controllers.addition import run_addition_quiz
        from unittest.mock import Mock, patch
        
        # Create mock container and services
        mock_container = Mock()
        mock_quiz_service = Mock()
        mock_container.quiz_svc = mock_quiz_service
        
        # Mock quiz session
        mock_quiz_session = Mock()
        mock_quiz_session.id = "session123"
        mock_quiz_service.start_quiz_session.return_value = mock_quiz_session
        
        # Create a limited generator
        generator = ProblemGenerator(1, 1, 1)  # Single easy problem
        
        # Mock the problem generation to return a predictable problem and control flow
        with patch.object(generator, 'get_next_problem', return_value=("1 + 1", 2)), \
             patch.object(generator, 'has_more_problems', side_effect=[True, False]), \
             patch("time.time", side_effect=[0, 1, 2, 3]), \
             patch("builtins.input", side_effect=["", "2"]):  # Enter to start, then correct answer
            
            correct, total, duration = run_addition_quiz(generator, mock_container, "user123")
            
            # Verify quiz session was started (covers line 197)
            mock_quiz_service.start_quiz_session.assert_called_once_with("user123", "addition", 1)
            
            # Verify quiz session was completed (covers line 280)
            mock_quiz_service.complete_session.assert_called_with("session123")
            
            # Verify answer was recorded (covers line 258)
            mock_quiz_service.record_answer.assert_called_once()
            
            assert correct == 1
            assert total == 1

    def test_run_quiz_exit_with_session_completion(self):
        """Test run_quiz exit command completes session."""
        from src.presentation.controllers.addition import run_addition_quiz
        from unittest.mock import Mock, patch
        
        # Create mock container and services
        mock_container = Mock()
        mock_quiz_service = Mock()
        mock_container.quiz_svc = mock_quiz_service
        
        # Mock quiz session
        mock_quiz_session = Mock()
        mock_quiz_session.id = "session123"
        mock_quiz_service.start_quiz_session.return_value = mock_quiz_session
        
        # Create an unlimited generator
        generator = ProblemGenerator(1, 1, 0)  # 0 means unlimited
        
        # Mock time and input - exit immediately
        with patch("time.time", side_effect=[0, 1, 2]), \
             patch("builtins.input", side_effect=["", "exit"]):  # Enter to start, then exit
            
            correct, total, duration = run_addition_quiz(generator, mock_container, "user123")
            
            # Verify session was completed on exit (covers line 229)
            mock_quiz_service.complete_session.assert_called_with("session123")
            
            assert correct == 0
            assert total == 0

    def test_run_quiz_stop_with_session_completion(self):
        """Test run_quiz stop command completes session."""
        from src.presentation.controllers.addition import run_addition_quiz
        from unittest.mock import Mock, patch
        
        # Create mock container and services
        mock_container = Mock()
        mock_quiz_service = Mock()
        mock_container.quiz_svc = mock_quiz_service
        
        # Mock quiz session
        mock_quiz_session = Mock()
        mock_quiz_session.id = "session123"
        mock_quiz_service.start_quiz_session.return_value = mock_quiz_session
        
        # Create an unlimited generator
        generator = ProblemGenerator(1, 1, 0)  # 0 means unlimited
        
        # Mock time and input - stop immediately
        with patch("time.time", side_effect=[0, 1, 2]), \
             patch("builtins.input", side_effect=["", "stop"]):  # Enter to start, then stop
            
            correct, total, duration = run_addition_quiz(generator, mock_container, "user123")
            
            # Verify session was completed on stop (covers line 236)
            mock_quiz_service.complete_session.assert_called_with("session123")
            
            assert correct == 0
            assert total == 0

    def test_run_quiz_next_records_skipped_attempt(self):
        """Test run_quiz next command records skipped attempt."""
        from src.presentation.controllers.addition import run_addition_quiz
        from unittest.mock import Mock, patch
        
        # Create mock container and services
        mock_container = Mock()
        mock_quiz_service = Mock()
        mock_container.quiz_svc = mock_quiz_service
        
        # Mock quiz session
        mock_quiz_session = Mock()
        mock_quiz_session.id = "session123"
        mock_quiz_service.start_quiz_session.return_value = mock_quiz_session
        
        # Create a limited generator
        generator = ProblemGenerator(1, 1, 1)  # Single easy problem
        
        # Mock time and input - skip the problem
        with patch("time.time", side_effect=[0, 1, 2, 3]), \
             patch("builtins.input", side_effect=["", "next"]):  # Enter to start, then skip
            
            correct, total, duration = run_addition_quiz(generator, mock_container, "user123")
            
            # Verify skipped attempt was recorded (covers lines 243-244)
            mock_quiz_service.record_answer.assert_called_once()
            record_args = mock_quiz_service.record_answer.call_args[0]  # positional args
            assert record_args[2] is None  # Third argument (user_answer) is None for skipped
            
            # Verify session was completed when all problems done (covers line 280)
            mock_quiz_service.complete_session.assert_called_with("session123")
            
            assert correct == 0
            assert total == 0

    def test_run_quiz_without_container_no_session_management(self):
        """Test run_quiz without container doesn't try session management."""
        from src.presentation.controllers.addition import run_addition_quiz
        from unittest.mock import patch
        
        # Create a limited generator
        generator = ProblemGenerator(1, 1, 1)  # Single easy problem
        
        # Mock time and input
        with patch("time.time", side_effect=[0, 1, 2, 3, 4, 5]), \
             patch("builtins.input", side_effect=["", "9", "stop"]):  # Enter to start, correct answer (9+0=9), then stop
            
            correct, total, duration = run_addition_quiz(generator, None, None)
            
            # Should work without error despite no container
            assert correct == 1
            assert total == 1

    def test_addition_mode_with_container_and_user(self):
        """Test addition_mode with container and user for session management."""
        from src.presentation.controllers.addition import addition_mode
        from unittest.mock import Mock, patch
        
        # Create mock container and services
        mock_container = Mock()
        mock_quiz_service = Mock()
        mock_container.quiz_svc = mock_quiz_service
        
        # Mock quiz session
        mock_quiz_session = Mock()
        mock_quiz_session.id = "session123"
        mock_quiz_service.start_quiz_session.return_value = mock_quiz_session
        
        # Mock all the dependencies
        with patch("src.presentation.controllers.addition.get_difficulty_range") as mock_get_difficulty, \
             patch("src.presentation.controllers.addition.get_num_problems") as mock_get_count, \
             patch("src.presentation.controllers.addition.run_addition_quiz") as mock_run_quiz, \
             patch("src.presentation.controllers.addition.show_results") as mock_show_results, \
             patch("builtins.print") as mock_print:
            
            mock_get_difficulty.return_value = (1, 3)
            mock_get_count.return_value = 5
            mock_run_quiz.return_value = (4, 5, 120.0)
            
            addition_mode(mock_container, "user123")
            
            # Verify run_quiz was called with container and user_id
            mock_run_quiz.assert_called_once()
            args = mock_run_quiz.call_args[0]
            assert args[1] == mock_container  # container
            assert args[2] == "user123"  # user_id
