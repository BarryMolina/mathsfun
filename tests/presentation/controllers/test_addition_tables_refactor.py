#!/usr/bin/env python3
"""Tests for refactored addition tables to ensure backward compatibility."""

import pytest
from unittest.mock import Mock, patch, call

from src.presentation.controllers.addition_tables import (
    get_addition_table_range,
    AdditionTableGenerator,
    run_addition_table_quiz,
    practice_addition_specific_range,
    addition_tables_mode,
    get_facts_needing_remedial_review,
    conduct_remedial_review,
    review_due_facts,
)


class TestBackwardCompatibility:
    """Test that refactored addition tables maintain backward compatibility."""
    
    def test_addition_table_generator_basic_functionality(self):
        """Test that AdditionTableGenerator still works as expected."""
        generator = AdditionTableGenerator(1, 3, randomize=False)
        
        assert generator.get_operation_symbol() == "+"
        assert generator.calculate_result(2, 3) == 5
        assert generator.total_problems == 9  # 3x3 grid
        
        # Check first few problems
        problem1, answer1 = generator.get_next_problem()
        assert problem1 == "1 + 1"
        assert answer1 == 2
        
        problem2, answer2 = generator.get_next_problem()
        assert problem2 == "1 + 2"
        assert answer2 == 3
    
    def test_addition_table_generator_inherits_base_class(self):
        """Test that AdditionTableGenerator properly inherits from base class."""
        from src.presentation.controllers.math_tables_base import MathTableGenerator
        
        generator = AdditionTableGenerator(2, 4, randomize=False)
        assert isinstance(generator, MathTableGenerator)
        
        # Should have base class methods
        assert hasattr(generator, 'has_more_problems')
        assert hasattr(generator, 'get_total_generated')
        assert hasattr(generator, 'get_progress_display')
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_get_addition_table_range(self, mock_input):
        """Test addition table range input still works."""
        mock_input.side_effect = ["1", "10"]
        
        low, high = get_addition_table_range()
        
        assert low == 1
        assert high == 10
    
    @patch('src.presentation.controllers.math_tables_base._run_quiz_session')
    def test_run_addition_table_quiz_still_works(self, mock_quiz_session):
        """Test that run_addition_table_quiz maintains same interface."""
        mock_quiz_session.return_value = (5, 6, 1, 30.0, [(2, 3, True, 1000, 0)])
        
        generator = AdditionTableGenerator(1, 2, randomize=False)
        result = run_addition_table_quiz(generator)
        
        assert result == (5, 6, 1, 30.0, [(2, 3, True, 1000, 0)])
        mock_quiz_session.assert_called_once()
    
    @patch('src.presentation.controllers.math_tables_base.tables_mode_workflow')
    def test_addition_tables_mode_uses_workflow(self, mock_workflow):
        """Test that addition_tables_mode uses the common workflow."""
        mock_container = Mock()
        mock_user = Mock()
        
        addition_tables_mode(mock_container, mock_user)
        
        mock_workflow.assert_called_once()
        args = mock_workflow.call_args[0]
        assert args[0] == "Addition"  # operation name
    
    def test_deprecated_functions_still_exist(self):
        """Test that deprecated functions still exist for backward compatibility."""
        from src.presentation.controllers.addition_tables import (
            get_addition_tables_choice,
            practice_specific_range,
            show_review_results,
        )
        
        # Should not raise ImportError
        assert callable(get_addition_tables_choice)
        assert callable(practice_specific_range)
        assert callable(show_review_results)


class TestAdditionSpecificFunctionality:
    """Test addition-specific functionality works correctly."""
    
    @patch('src.presentation.controllers.addition_tables.get_addition_table_range')
    @patch('src.presentation.controllers.math_tables_base.get_order_preference')
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.addition_tables.run_addition_table_quiz')
    @patch('src.presentation.controllers.math_tables_base.show_results_with_fact_insights')
    def test_practice_addition_specific_range(self, mock_show_results, mock_quiz, mock_prompt,
                                            mock_order, mock_range):
        """Test practice specific range functionality."""
        mock_range.return_value = (2, 4)
        mock_order.return_value = True  # Random
        mock_prompt.return_value = True
        mock_quiz.return_value = (6, 8, 1, 25.0, [(2, 3, True, 1500, 0)])
        
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        
        practice_addition_specific_range(mock_container, mock_user)
        
        # Verify quiz was called with correct generator
        mock_quiz.assert_called_once()
        args = mock_quiz.call_args[0]
        generator = args[0]
        assert isinstance(generator, AdditionTableGenerator)
        assert generator.low == 2
        assert generator.high == 4
        assert generator.randomize is True
        
        # Verify fact tracking with addition operation
        mock_container.math_fact_svc.analyze_session_performance.assert_called_once_with(
            "user123", [(2, 3, True, 1500, 0)], "+"
        )
    
    def test_get_facts_needing_remedial_review_addition_only(self):
        """Test that remedial review only gets addition facts."""
        mock_service = Mock()
        
        # Mix of addition and subtraction facts
        mock_performances = [
            Mock(fact_key="5+3", ease_factor=1.5, accuracy=0.6, total_attempts=5),  # Addition - needs review
            Mock(fact_key="8-2", ease_factor=1.0, accuracy=0.4, total_attempts=4),  # Subtraction - ignore
            Mock(fact_key="7+4", ease_factor=2.5, accuracy=0.9, total_attempts=3),  # Addition - good
            Mock(fact_key="10+6", ease_factor=1.7, accuracy=0.65, total_attempts=4), # Addition - needs review
        ]
        mock_service.get_all_user_performances.return_value = mock_performances
        
        remedial_facts = get_facts_needing_remedial_review(mock_service, "user123")
        
        # Should only return addition facts that need review
        assert len(remedial_facts) == 2
        assert (5, 3) in remedial_facts
        assert (10, 6) in remedial_facts
        assert (8, 2) not in remedial_facts  # Subtraction fact ignored
    
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.math_tables_base._run_quiz_session')
    def test_conduct_remedial_review_addition(self, mock_quiz, mock_prompt):
        """Test conducting remedial review for addition facts."""
        mock_prompt.return_value = True
        mock_quiz.return_value = (2, 2, 0, 15.0, [(5, 3, True, 1200, 0), (7, 2, True, 800, 1)])
        
        remedial_facts = [(5, 3), (7, 2)]
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        
        conduct_remedial_review(remedial_facts, mock_container, mock_user)
        
        # Verify quiz problems are addition
        args = mock_quiz.call_args[0]
        problems, config = args
        expected_problems = [("5 + 3", 8), ("7 + 2", 9)]
        assert problems == expected_problems
        
        # Verify config for addition
        assert "Remedial Review - Addition Facts" in config.header_lines[0]
        assert config.operation_symbol == "+"
        
        # Verify performance tracking with addition operation
        mock_container.math_fact_svc.analyze_session_performance.assert_called_once_with(
            "user123", [(5, 3, True, 1200, 0), (7, 2, True, 800, 1)], "+"
        )


class TestIntegrationWithOldCode:
    """Test integration with any existing code that might depend on old interfaces."""
    
    def test_old_import_patterns_still_work(self):
        """Test that old import patterns still work."""
        # These should not raise ImportError
        from src.presentation.controllers.addition_tables import addition_tables_mode
        from src.presentation.controllers.addition_tables import AdditionTableGenerator
        from src.presentation.controllers.addition_tables import run_addition_table_quiz
        
        assert callable(addition_tables_mode)
        assert AdditionTableGenerator is not None
        assert callable(run_addition_table_quiz)
    
    def test_generator_interface_compatibility(self):
        """Test that generator interface is compatible with old expectations."""
        generator = AdditionTableGenerator(1, 3, randomize=False)
        
        # Old interface expectations
        assert hasattr(generator, 'low')
        assert hasattr(generator, 'high')
        assert hasattr(generator, 'randomize')
        assert hasattr(generator, 'get_next_problem')
        assert hasattr(generator, 'has_more_problems')
        assert hasattr(generator, 'get_total_generated')
        assert hasattr(generator, 'get_progress_display')
        
        # Values should be preserved
        assert generator.low == 1
        assert generator.high == 3
        assert generator.randomize is False