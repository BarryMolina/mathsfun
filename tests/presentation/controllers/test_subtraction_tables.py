#!/usr/bin/env python3
"""Tests for subtraction tables functionality."""

import pytest
from unittest.mock import Mock, patch, call
from typing import List, Tuple

from src.presentation.controllers.subtraction_tables import (
    get_subtraction_table_ranges,
    SubtractionTableGenerator,
    run_subtraction_table_quiz,
    practice_subtraction_specific_range,
    get_facts_needing_remedial_review,
    conduct_remedial_review,
    review_due_facts,
    subtraction_tables_mode,
)


class TestGetSubtractionTableRanges:
    """Test dual-range input for subtraction tables."""
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_valid_range_input(self, mock_input):
        """Test valid dual-range input."""
        mock_input.side_effect = ["1", "10", "0", "9"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 10
        assert offset_low == 0
        assert offset_high == 9
        assert mock_input.call_count == 4
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_invalid_subtrahend_range(self, mock_input):
        """Test handling of invalid subtrahend range."""
        # High < low, then valid input
        mock_input.side_effect = ["10", "1", "1", "10", "0", "5"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 10
        assert offset_low == 0
        assert offset_high == 5
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_out_of_bounds_values(self, mock_input):
        """Test handling of out-of-bounds values."""
        # Out of bounds, then valid
        mock_input.side_effect = ["101", "-1", "1", "10", "0", "9"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 10
        assert offset_low == 0
        assert offset_high == 9
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_invalid_offset_range(self, mock_input):
        """Test handling of invalid offset range."""
        # Valid subtrahend, invalid offset (high < low), then valid offset
        mock_input.side_effect = ["1", "5", "10", "0", "0", "5"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 5
        assert offset_low == 0
        assert offset_high == 5
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_large_problem_count_warning(self, mock_input):
        """Test warning for very large problem counts."""
        # Large ranges that would create >10000 problems
        mock_input.side_effect = ["1", "100", "0", "100", "n", "1", "10", "0", "9"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        # Should recursively call and get smaller ranges
        assert subtrahend_low == 1
        assert subtrahend_high == 10
        assert offset_low == 0
        assert offset_high == 9
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_large_problem_count_confirmation(self, mock_input):
        """Test confirming large problem count."""
        # Large ranges with confirmation
        mock_input.side_effect = ["1", "50", "0", "50", "y"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 50
        assert offset_low == 0
        assert offset_high == 50
    
    @patch('src.presentation.cli.ui.get_user_input')
    def test_non_numeric_input(self, mock_input):
        """Test handling of non-numeric input."""
        mock_input.side_effect = ["invalid", "abc", "1", "10", "xyz", "0", "9"]
        
        subtrahend_low, subtrahend_high, offset_low, offset_high = get_subtraction_table_ranges()
        
        assert subtrahend_low == 1
        assert subtrahend_high == 10
        assert offset_low == 0
        assert offset_high == 9


class TestSubtractionTableGenerator:
    """Test SubtractionTableGenerator class."""
    
    def test_basic_generation(self):
        """Test basic subtraction problem generation."""
        generator = SubtractionTableGenerator(1, 3, 0, 2, randomize=False)
        
        assert generator.get_operation_symbol() == "-"
        assert generator.calculate_result(5, 3) == 2
        assert generator.total_problems == 9  # 3 subtrahends × 3 offsets
    
    def test_problem_generation_content(self):
        """Test that generated problems are correct."""
        generator = SubtractionTableGenerator(2, 3, 1, 2, randomize=False)
        
        expected_problems = [
            ("3 - 2", 1),  # 2+1 - 2 = 1
            ("4 - 2", 2),  # 2+2 - 2 = 2
            ("4 - 3", 1),  # 3+1 - 3 = 1
            ("5 - 3", 2),  # 3+2 - 3 = 2
        ]
        
        actual_problems = []
        while generator.has_more_problems():
            problem, answer = generator.get_next_problem()
            actual_problems.append((problem, answer))
        
        assert actual_problems == expected_problems
    
    def test_non_negative_results_guarantee(self):
        """Test that all generated problems have non-negative results."""
        generator = SubtractionTableGenerator(1, 20, 0, 50, randomize=False)
        
        while generator.has_more_problems():
            problem, answer = generator.get_next_problem()
            assert answer >= 0, f"Negative result: {problem} = {answer}"
    
    def test_randomized_problems(self):
        """Test that randomization works."""
        problems_set1 = []
        problems_set2 = []
        
        # Generate same problems twice with randomization
        for _ in range(2):
            generator = SubtractionTableGenerator(1, 5, 0, 5, randomize=True)
            problems = []
            while generator.has_more_problems():
                problems.append(generator.get_next_problem())
            if not problems_set1:
                problems_set1 = problems
            else:
                problems_set2 = problems
        
        # Same content, potentially different order
        assert sorted(problems_set1) == sorted(problems_set2)
        # With 36 problems, very unlikely to have same order if truly random
        if len(problems_set1) > 10:
            # Allow some chance they could be the same, but very unlikely
            assert problems_set1 != problems_set2 or len(problems_set1) < 5
    
    def test_configuration_summary(self):
        """Test configuration summary display."""
        generator = SubtractionTableGenerator(1, 10, 0, 9, randomize=False)
        summary = generator.get_configuration_summary()
        assert "Subtrahend: 1-10" in summary
        assert "Offset: 0-9" in summary
        
        # Single values
        generator2 = SubtractionTableGenerator(5, 5, 3, 3, randomize=False)
        summary2 = generator2.get_configuration_summary()
        assert "Subtrahend: 5" in summary2
        assert "Offset: 3" in summary2
    
    def test_range_input_prompts(self):
        """Test range input prompt messages."""
        generator = SubtractionTableGenerator(1, 10, 0, 5, randomize=False)
        prompts = generator.get_range_input_prompt()
        
        assert len(prompts) == 2
        assert "subtrahend" in prompts[0].lower()
        assert "offset" in prompts[1].lower()


class TestRunSubtractionTableQuiz:
    """Test subtraction table quiz functionality."""
    
    def test_quiz_execution(self):
        """Test basic quiz execution."""
        generator = SubtractionTableGenerator(3, 3, 2, 2, randomize=False)
        
        # Mock the quiz session
        with patch('src.presentation.controllers.subtraction_tables._run_quiz_session') as mock_quiz:
            mock_quiz.return_value = (1, 1, 0, 5.0, [(5, 3, True, 1000, 0)])
            
            correct, total, skipped, duration, attempts = run_subtraction_table_quiz(generator)
        
        mock_quiz.assert_called_once()
        args, kwargs = mock_quiz.call_args
        problems, config = args
        
        # Check problems were generated
        assert len(problems) == 1
        assert problems[0] == ("5 - 3", 2)  # 3+2-3 = 2
        
        # Check config
        assert "Subtraction Table" in config.header_lines[0]
        assert config.operation_symbol == "-"
        assert "1 problems to solve" in config.header_lines[1]
        assert "All answers will be non-negative" in config.header_lines[2]
    
    def test_quiz_with_fact_service(self):
        """Test quiz with fact tracking service."""
        generator = SubtractionTableGenerator(2, 2, 1, 1, randomize=False)
        mock_service = Mock()
        
        with patch('src.presentation.controllers.subtraction_tables._run_quiz_session') as mock_quiz:
            mock_quiz.return_value = (1, 1, 0, 3.0, [(3, 2, True, 1500, 0)])
            
            run_subtraction_table_quiz(generator, mock_service, "user123")
        
        args, kwargs = mock_quiz.call_args
        problems, config = args
        
        assert config.math_fact_service == mock_service
        assert config.user_id == "user123"
    
    def test_quiz_configuration_summary(self):
        """Test quiz header includes configuration summary."""
        generator = SubtractionTableGenerator(5, 8, 0, 3, randomize=True)
        
        with patch('src.presentation.controllers.subtraction_tables._run_quiz_session') as mock_quiz:
            mock_quiz.return_value = (1, 1, 0, 2.0, [])
            
            run_subtraction_table_quiz(generator)
        
        args, kwargs = mock_quiz.call_args
        problems, config = args
        
        header = config.header_lines[0]
        assert "Subtrahend: 5-8" in header
        assert "Offset: 0-3" in header
        assert "random order" in header


class TestPracticeSubtractionSpecificRange:
    """Test practice specific range functionality."""
    
    @patch('src.presentation.controllers.subtraction_tables.get_subtraction_table_ranges')
    @patch('src.presentation.controllers.math_tables_base.get_order_preference')
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.subtraction_tables.run_subtraction_table_quiz')
    @patch('src.presentation.controllers.math_tables_base.show_results_with_fact_insights')
    def test_successful_practice_session(self, mock_show_results, mock_quiz, mock_prompt, 
                                       mock_order, mock_ranges):
        """Test successful practice session."""
        mock_ranges.return_value = (1, 5, 0, 4)
        mock_order.return_value = False  # Sequential
        mock_prompt.return_value = True
        mock_quiz.return_value = (10, 12, 2, 30.0, [(1, 1, True, 1000, 0)])
        
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        
        practice_subtraction_specific_range(mock_container, mock_user)
        
        # Verify quiz was run
        mock_quiz.assert_called_once()
        args, kwargs = mock_quiz.call_args
        generator = args[0]
        assert isinstance(generator, SubtractionTableGenerator)
        assert generator.subtrahend_low == 1
        assert generator.subtrahend_high == 5
        assert generator.offset_low == 0
        assert generator.offset_high == 4
        assert generator.randomize is False
        
        # Verify fact service was called
        mock_container.math_fact_svc.analyze_session_performance.assert_called_once()
        
        # Verify results were shown
        mock_show_results.assert_called_once()
    
    @patch('src.presentation.controllers.subtraction_tables.get_subtraction_table_ranges')
    @patch('src.presentation.controllers.math_tables_base.get_order_preference')
    @patch('src.presentation.controllers.session.prompt_start_session')
    def test_user_cancels_session(self, mock_prompt, mock_order, mock_ranges):
        """Test when user cancels the session."""
        mock_ranges.return_value = (1, 3, 0, 2)
        mock_order.return_value = True  # Random
        mock_prompt.return_value = False  # User cancels
        
        with patch('src.presentation.controllers.subtraction_tables.run_subtraction_table_quiz') as mock_quiz:
            practice_subtraction_specific_range()
            mock_quiz.assert_not_called()
    
    @patch('src.presentation.controllers.subtraction_tables.get_subtraction_table_ranges')
    @patch('src.presentation.controllers.math_tables_base.get_order_preference') 
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.subtraction_tables.run_subtraction_table_quiz')
    def test_without_container_and_user(self, mock_quiz, mock_prompt, mock_order, mock_ranges):
        """Test practice without container and user (no fact tracking)."""
        mock_ranges.return_value = (2, 4, 1, 3)
        mock_order.return_value = False
        mock_prompt.return_value = True
        mock_quiz.return_value = (5, 6, 1, 15.0, [])
        
        practice_subtraction_specific_range()  # No container/user
        
        # Verify quiz was called without fact service
        args, kwargs = mock_quiz.call_args
        assert args[1] is None  # math_fact_service
        assert args[2] is None  # user_id


class TestGetFactsNeedingRemedialReview:
    """Test identification of facts needing remedial review."""
    
    def test_identifies_struggling_facts(self):
        """Test identification of struggling subtraction facts."""
        mock_service = Mock()
        
        # Mock performances with various levels of difficulty
        mock_performances = [
            Mock(fact_key="10-3", ease_factor=1.5, accuracy=0.6, total_attempts=5),  # Needs remedial
            Mock(fact_key="8-2", ease_factor=2.5, accuracy=0.9, total_attempts=3),   # Good
            Mock(fact_key="12+5", ease_factor=1.0, accuracy=0.4, total_attempts=4),  # Addition - ignore
            Mock(fact_key="15-7", ease_factor=1.7, accuracy=0.65, total_attempts=4), # Needs remedial  
            Mock(fact_key="9-4", ease_factor=2.0, accuracy=0.8, total_attempts=2),   # Good
        ]
        mock_service.get_all_user_performances.return_value = mock_performances
        
        remedial_facts = get_facts_needing_remedial_review(mock_service, "user123")
        
        # Should identify the two struggling subtraction facts
        assert len(remedial_facts) == 2
        assert (10, 3) in remedial_facts
        assert (15, 7) in remedial_facts
        assert (8, 2) not in remedial_facts  # Good performance
        assert (9, 4) not in remedial_facts  # Good performance
    
    def test_handles_malformed_fact_keys(self):
        """Test handling of malformed fact keys."""
        mock_service = Mock()
        
        mock_performances = [
            Mock(fact_key="10-3", ease_factor=1.5, accuracy=0.6, total_attempts=5),    # Valid
            Mock(fact_key="invalid-key-format", ease_factor=1.0, accuracy=0.3, total_attempts=4),  # Invalid
            Mock(fact_key="abc-def", ease_factor=1.2, accuracy=0.5, total_attempts=3), # Invalid numbers
            Mock(fact_key="5-", ease_factor=1.1, accuracy=0.4, total_attempts=2),      # Missing operand
        ]
        mock_service.get_all_user_performances.return_value = mock_performances
        
        remedial_facts = get_facts_needing_remedial_review(mock_service, "user123")
        
        # Should only return the valid fact
        assert len(remedial_facts) == 1
        assert (10, 3) in remedial_facts
    
    def test_no_subtraction_facts(self):
        """Test when no subtraction facts exist."""
        mock_service = Mock()
        
        mock_performances = [
            Mock(fact_key="5+3", ease_factor=1.5, accuracy=0.6, total_attempts=5),  # Addition
            Mock(fact_key="8+2", ease_factor=1.0, accuracy=0.3, total_attempts=4),  # Addition
        ]
        mock_service.get_all_user_performances.return_value = mock_performances
        
        remedial_facts = get_facts_needing_remedial_review(mock_service, "user123")
        
        assert len(remedial_facts) == 0


class TestConductRemedialReview:
    """Test remedial review functionality."""
    
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.math_tables_base._run_quiz_session')
    def test_conducts_remedial_review(self, mock_quiz, mock_prompt):
        """Test conducting remedial review session."""
        mock_prompt.return_value = True
        mock_quiz.return_value = (2, 3, 0, 20.0, [(10, 3, True, 1000, 1), (15, 7, False, 2000, 2)])
        
        remedial_facts = [(10, 3), (15, 7), (12, 5)]
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        
        conduct_remedial_review(remedial_facts, mock_container, mock_user)
        
        # Verify quiz was run
        mock_quiz.assert_called_once()
        args, kwargs = mock_quiz.call_args
        problems, config = args
        
        # Check problems
        expected_problems = [("10 - 3", 7), ("15 - 7", 8), ("12 - 5", 7)]
        assert problems == expected_problems
        
        # Check config
        assert "Remedial Review - Subtraction Facts" in config.header_lines[0]
        assert config.operation_symbol == "-"
        assert config.show_results_on_exit is True
        
        # Verify performance tracking
        mock_container.math_fact_svc.analyze_session_performance.assert_called_once()
    
    def test_no_remedial_facts_needed(self):
        """Test when no facts need remedial review."""
        remedial_facts = []
        
        with patch('src.presentation.controllers.session.prompt_start_session') as mock_prompt:
            conduct_remedial_review(remedial_facts)
            mock_prompt.assert_not_called()
    
    @patch('src.presentation.controllers.session.prompt_start_session')
    def test_user_cancels_remedial_review(self, mock_prompt):
        """Test when user cancels remedial review."""
        mock_prompt.return_value = False
        remedial_facts = [(8, 3), (9, 2)]
        
        with patch('src.presentation.controllers.math_tables_base._run_quiz_session') as mock_quiz:
            conduct_remedial_review(remedial_facts)
            mock_quiz.assert_not_called()


class TestReviewDueFacts:
    """Test review due facts functionality."""
    
    def test_no_user_signed_in(self):
        """Test when no user is signed in."""
        with patch('builtins.print') as mock_print:
            review_due_facts()
            mock_print.assert_called_with("❌ Please sign in to access spaced repetition review")
    
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.math_tables_base._run_quiz_session')
    @patch('src.presentation.controllers.subtraction_tables.get_facts_needing_remedial_review')
    def test_review_with_scheduled_and_remedial_facts(self, mock_remedial, mock_quiz, mock_prompt):
        """Test review with both scheduled and remedial facts."""
        mock_prompt.return_value = True
        mock_quiz.return_value = (3, 4, 0, 25.0, [])
        mock_remedial.return_value = [(12, 5), (8, 3)]
        
        # Mock scheduled facts (subtraction only)
        mock_scheduled_perf1 = Mock(fact_key="10-4")
        mock_scheduled_perf2 = Mock(fact_key="7+2")  # Addition - should be filtered out
        mock_scheduled_perf3 = Mock(fact_key="15-8")
        scheduled_facts = [mock_scheduled_perf1, mock_scheduled_perf2, mock_scheduled_perf3]
        
        mock_container = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_container.math_fact_svc = Mock()
        mock_container.math_fact_svc.get_facts_due_for_review.return_value = scheduled_facts
        
        review_due_facts(mock_container, mock_user)
        
        # Verify quiz was run
        mock_quiz.assert_called_once()
        args, kwargs = mock_quiz.call_args
        problems, config = args
        
        # Should have 2 scheduled subtraction + 2 remedial = 4 problems
        expected_problems = [("10 - 4", 6), ("15 - 8", 7), ("12 - 5", 7), ("8 - 3", 5)]
        assert problems == expected_problems
        
        # Check config
        assert "Review Due Facts - Subtraction" in config.header_lines[0]
        assert config.operation_symbol == "-"
        assert config.show_results_on_exit is True
    
    @patch('src.presentation.controllers.subtraction_tables.get_facts_needing_remedial_review')
    def test_no_facts_due(self, mock_remedial):
        """Test when no facts are due for review."""
        mock_remedial.return_value = []
        
        mock_container = Mock()
        mock_user = Mock()
        mock_container.math_fact_svc = Mock()
        mock_container.math_fact_svc.get_facts_due_for_review.return_value = []
        
        with patch('builtins.print') as mock_print:
            review_due_facts(mock_container, mock_user)
            # Should print no facts due message
            assert any("Excellent! No subtraction facts are due" in str(call) for call in mock_print.call_args_list)
    
    @patch('src.presentation.controllers.session.prompt_start_session')
    @patch('src.presentation.controllers.subtraction_tables.get_facts_needing_remedial_review')
    def test_user_cancels_review(self, mock_remedial, mock_prompt):
        """Test when user cancels the review session."""
        mock_prompt.return_value = False
        mock_remedial.return_value = [(5, 2)]
        
        mock_container = Mock()
        mock_user = Mock()
        mock_container.math_fact_svc = Mock()
        mock_container.math_fact_svc.get_facts_due_for_review.return_value = [Mock(fact_key="8-3")]
        
        with patch('src.presentation.controllers.math_tables_base._run_quiz_session') as mock_quiz:
            review_due_facts(mock_container, mock_user)
            mock_quiz.assert_not_called()


class TestSubtractionTablesMode:
    """Test main subtraction tables mode."""
    
    @patch('src.presentation.controllers.math_tables_base.tables_mode_workflow')
    def test_subtraction_tables_mode_calls_workflow(self, mock_workflow):
        """Test that subtraction tables mode calls the common workflow."""
        mock_container = Mock()
        mock_user = Mock()
        
        subtraction_tables_mode(mock_container, mock_user)
        
        mock_workflow.assert_called_once()
        args, kwargs = mock_workflow.call_args
        operation_name, practice_func, review_func, container, user = args
        
        assert operation_name == "Subtraction"
        assert container == mock_container
        assert user == mock_user
        # Functions should be the correct ones
        assert practice_func == practice_subtraction_specific_range
        assert review_func == review_due_facts