#!/usr/bin/env python3
"""Tests for math tables base classes and common functionality."""

import pytest
from unittest.mock import Mock, patch, call
from typing import List, Tuple

from src.presentation.controllers.math_tables_base import (
    QuizSessionConfig,
    MathTableGenerator,
    _run_quiz_session,
    get_order_preference,
    get_tables_choice,
    tables_mode_workflow,
    show_results_with_fact_insights,
)


class ConcreteMathTableGenerator(MathTableGenerator):
    """Concrete implementation for testing abstract base class."""
    
    def __init__(self, problems: List[Tuple[str, int]], randomize: bool = False):
        super().__init__(randomize)
        self.test_problems = problems
        self.initialize_problems()
    
    def get_operation_symbol(self) -> str:
        return "+"
    
    def calculate_result(self, operand1: int, operand2: int) -> int:
        return operand1 + operand2
    
    def generate_problems(self) -> List[Tuple[str, int]]:
        return self.test_problems
    
    def get_range_input_prompt(self) -> List[str]:
        return ["Enter test range"]


class TestQuizSessionConfig:
    """Test QuizSessionConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = QuizSessionConfig(header_lines=["Test Header"])
        
        assert config.header_lines == ["Test Header"]
        assert config.commands_text == "Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)"
        assert config.progress_format == "Problem {current}/{total}"
        assert config.show_results_on_exit is False
        assert config.math_fact_service is None
        assert config.user_id is None
        assert config.total_facts is None
        assert config.operation_symbol == "+"
    
    def test_custom_values(self):
        """Test custom configuration values."""
        mock_service = Mock()
        config = QuizSessionConfig(
            header_lines=["Custom Header"],
            commands_text="Custom commands",
            progress_format="Custom {current}/{total}",
            show_results_on_exit=True,
            math_fact_service=mock_service,
            user_id="test_user",
            total_facts=100,
            operation_symbol="-"
        )
        
        assert config.header_lines == ["Custom Header"]
        assert config.commands_text == "Custom commands"
        assert config.progress_format == "Custom {current}/{total}"
        assert config.show_results_on_exit is True
        assert config.math_fact_service == mock_service
        assert config.user_id == "test_user"
        assert config.total_facts == 100
        assert config.operation_symbol == "-"


class TestMathTableGenerator:
    """Test MathTableGenerator abstract base class."""
    
    def test_concrete_implementation(self):
        """Test concrete implementation works correctly."""
        problems = [("2 + 3", 5), ("4 + 1", 5)]
        generator = ConcreteMathTableGenerator(problems)
        
        assert generator.get_operation_symbol() == "+"
        assert generator.calculate_result(2, 3) == 5
        assert generator.has_more_problems()
        assert generator.get_total_generated() == 0
        
        problem1, answer1 = generator.get_next_problem()
        assert problem1 == "2 + 3"
        assert answer1 == 5
        assert generator.get_total_generated() == 1
        
        problem2, answer2 = generator.get_next_problem()
        assert problem2 == "4 + 1"
        assert answer2 == 5
        assert generator.get_total_generated() == 2
        
        assert not generator.has_more_problems()
    
    def test_randomized_problems(self):
        """Test randomized problem order."""
        problems = [("1 + 1", 2), ("2 + 2", 4), ("3 + 3", 6)]
        
        with patch('random.shuffle') as mock_shuffle:
            generator = ConcreteMathTableGenerator(problems, randomize=True)
            mock_shuffle.assert_called_once()
    
    def test_sequential_problems(self):
        """Test sequential problem order (no shuffling)."""
        problems = [("1 + 1", 2), ("2 + 2", 4), ("3 + 3", 6)]
        
        with patch('random.shuffle') as mock_shuffle:
            generator = ConcreteMathTableGenerator(problems, randomize=False)
            mock_shuffle.assert_not_called()
    
    def test_out_of_problems_error(self):
        """Test error when trying to get problem beyond available."""
        problems = [("1 + 1", 2)]
        generator = ConcreteMathTableGenerator(problems)
        
        # Get the only problem
        generator.get_next_problem()
        
        # Should raise error when trying to get another
        with pytest.raises(IndexError, match="No more problems available"):
            generator.get_next_problem()
    
    def test_progress_display(self):
        """Test progress display formatting."""
        problems = [("1 + 1", 2), ("2 + 2", 4)]
        generator = ConcreteMathTableGenerator(problems)
        
        assert generator.get_progress_display() == "0/2"
        generator.get_next_problem()
        assert generator.get_progress_display() == "1/2"
        generator.get_next_problem()
        assert generator.get_progress_display() == "2/2"


class TestRunQuizSession:
    """Test the core quiz engine functionality."""
    
    def test_successful_quiz_completion(self):
        """Test completing a quiz with correct answers."""
        problems = [("2 + 3", 5), ("4 + 1", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', '5', '5']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2]):  # Mock timing
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 2
        assert total == 2
        assert skipped == 0
        assert duration == 2
        assert len(attempts) == 2
    
    def test_quiz_with_skip_commands(self):
        """Test quiz with 'next' (skip) commands."""
        problems = [("2 + 3", 5), ("4 + 1", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', 'next', '5']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert total == 1
        assert skipped == 1
        assert duration == 2
        assert len(attempts) == 1  # Only the correct answer should be recorded
    
    def test_quiz_with_incorrect_then_correct(self):
        """Test quiz with incorrect attempts followed by correct answer."""
        problems = [("2 + 3", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', '4', '6', '5']):  # wrong, wrong, correct
            with patch('time.time', side_effect=[0, 0, 1, 1, 2, 2, 3]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert total == 3  # 3 attempts total (2 wrong + 1 correct)
        assert skipped == 0
        assert duration == 3
        assert len(attempts) == 1
        # Check that incorrect attempts are tracked
        operand1, operand2, is_correct, response_time, incorrect_count = attempts[0]
        assert operand1 == 2
        assert operand2 == 3
        assert is_correct is True
        assert incorrect_count == 2  # Two incorrect attempts before the correct one
    
    def test_quiz_early_exit(self):
        """Test quiz with early exit command."""
        problems = [("2 + 3", 5), ("4 + 1", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', '5', 'exit']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert total == 1
        assert skipped == 0
        assert duration == 2
        assert len(attempts) == 1
    
    def test_quiz_stop_command(self):
        """Test quiz with stop command."""
        problems = [("2 + 3", 5), ("4 + 1", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', '5', 'stop']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert total == 1
        assert skipped == 0
        assert duration == 2
        assert len(attempts) == 1
    
    def test_invalid_input_handling(self):
        """Test handling of invalid input."""
        problems = [("2 + 3", 5)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="+"
        )
        
        with patch('builtins.input', side_effect=['', 'invalid', 'not_a_number', '5']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2, 2, 3]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert total == 1  # Invalid inputs don't count as attempts
        assert skipped == 0
    
    def test_subtraction_operation_parsing(self):
        """Test parsing of subtraction problems."""
        problems = [("10 - 3", 7)]
        config = QuizSessionConfig(
            header_lines=["Test Quiz"],
            operation_symbol="-"
        )
        
        with patch('builtins.input', side_effect=['', '7']):
            with patch('time.time', side_effect=[0, 0, 1, 1, 2]):
                correct, total, skipped, duration, attempts = _run_quiz_session(problems, config)
        
        assert correct == 1
        assert len(attempts) == 1
        operand1, operand2, is_correct, response_time, incorrect_count = attempts[0]
        assert operand1 == 10
        assert operand2 == 3
        assert is_correct is True


class TestOrderPreference:
    """Test order preference selection."""
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_sequential_order_selection(self, mock_input):
        """Test selecting sequential order."""
        mock_input.return_value = "1"
        
        result = get_order_preference()
        
        assert result is False  # Sequential = False
        mock_input.assert_called_once_with("Select order", "1")
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_random_order_selection(self, mock_input):
        """Test selecting random order."""
        mock_input.return_value = "2"
        
        result = get_order_preference()
        
        assert result is True  # Random = True
        mock_input.assert_called_once_with("Select order", "1")
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_invalid_then_valid_selection(self, mock_input):
        """Test invalid input followed by valid selection."""
        mock_input.side_effect = ["3", "invalid", "1"]
        
        result = get_order_preference()
        
        assert result is False
        assert mock_input.call_count == 3


class TestTablesChoice:
    """Test tables choice menu functionality."""
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_choice_with_signed_in_user(self, mock_input):
        """Test choice display with signed-in user and due facts."""
        mock_input.return_value = "1"
        mock_service = Mock()
        mock_service.get_facts_due_for_review.return_value = [Mock(), Mock()]  # 2 due facts
        
        result = get_tables_choice("Addition", mock_service, "user123")
        
        assert result == 1
        mock_service.get_facts_due_for_review.assert_called_once_with("user123", limit=100)
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_choice_without_user(self, mock_input):
        """Test choice display without signed-in user."""
        mock_input.return_value = "2"
        
        result = get_tables_choice("Subtraction")
        
        assert result == 2
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_invalid_choice_handling(self, mock_input):
        """Test handling of invalid menu choices."""
        mock_input.side_effect = ["5", "0", "invalid", "3"]
        
        result = get_tables_choice("Addition")
        
        assert result == 3
        assert mock_input.call_count == 4


class TestTablesWorkflow:
    """Test tables mode workflow functionality."""
    
    def test_workflow_practice_choice(self):
        """Test workflow with practice choice."""
        mock_practice = Mock()
        mock_review = Mock()
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        
        with patch('src.presentation.controllers.math_tables_base.get_tables_choice', return_value=1):
            tables_mode_workflow("Addition", mock_practice, mock_review, mock_container, mock_user)
        
        mock_practice.assert_called_once_with(mock_container, mock_user)
        mock_review.assert_not_called()
    
    def test_workflow_review_choice(self):
        """Test workflow with review choice."""
        mock_practice = Mock()
        mock_review = Mock()
        mock_container = Mock()
        mock_user = Mock()
        
        with patch('src.presentation.controllers.math_tables_base.get_tables_choice', return_value=2):
            tables_mode_workflow("Subtraction", mock_practice, mock_review, mock_container, mock_user)
        
        mock_review.assert_called_once_with(mock_container, mock_user)
        mock_practice.assert_not_called()
    
    def test_workflow_analytics_choice(self):
        """Test workflow with analytics choice."""
        mock_practice = Mock()
        mock_review = Mock()
        
        with patch('src.presentation.controllers.math_tables_base.get_tables_choice', return_value=3):
            with patch('src.presentation.controllers.math_tables_base.view_analytics_mode') as mock_analytics:
                tables_mode_workflow("Addition", mock_practice, mock_review)
                mock_analytics.assert_called_once()
    
    def test_workflow_return_choice(self):
        """Test workflow with return to main menu choice."""
        mock_practice = Mock()
        mock_review = Mock()
        
        with patch('src.presentation.controllers.math_tables_base.get_tables_choice', return_value=4):
            result = tables_mode_workflow("Addition", mock_practice, mock_review)
        
        assert result is None
        mock_practice.assert_not_called()
        mock_review.assert_not_called()
    
    def test_workflow_exception_handling(self):
        """Test workflow exception handling."""
        mock_practice = Mock(side_effect=Exception("Test error"))
        mock_review = Mock()
        
        with patch('src.presentation.controllers.math_tables_base.get_tables_choice', return_value=1):
            # Should not raise exception, should handle gracefully
            tables_mode_workflow("Addition", mock_practice, mock_review)


class TestShowResultsWithFactInsights:
    """Test results display with fact insights."""
    
    def test_results_without_fact_service(self):
        """Test results display without fact tracking."""
        generator = ConcreteMathTableGenerator([("1+1", 2)])
        
        with patch('src.presentation.controllers.math_tables_base.show_results') as mock_show:
            show_results_with_fact_insights(1, 1, 10.0, generator, 0, [])
        
        mock_show.assert_called_once_with(1, 1, 10.0, generator, skipped_count=0)
    
    def test_results_with_fact_insights(self):
        """Test results display with fact tracking and insights."""
        generator = ConcreteMathTableGenerator([("1+1", 2)])
        mock_service = Mock()
        session_attempts = [(1, 1, True, 1000, 0), (2, 2, False, 2000, 2)]
        
        with patch('src.presentation.controllers.math_tables_base.show_results') as mock_show:
            show_results_with_fact_insights(
                2, 2, 15.0, generator, 0, session_attempts, mock_service, "user123"
            )
        
        mock_show.assert_called_once()
        # Should print insights about session attempts
    
    def test_results_with_struggling_facts(self):
        """Test results display highlighting struggling facts."""
        generator = ConcreteMathTableGenerator([("1+1", 2)])
        mock_service = Mock()
        # Session with multiple incorrect attempts
        session_attempts = [(3, 4, True, 3000, 3), (5, 6, False, 4000, 1)]
        
        with patch('src.presentation.controllers.math_tables_base.show_results') as mock_show:
            show_results_with_fact_insights(
                1, 2, 20.0, generator, 1, session_attempts, mock_service, "user123"
            )
        
        mock_show.assert_called_once()
        # Should identify facts that struggled (multiple attempts or failed)