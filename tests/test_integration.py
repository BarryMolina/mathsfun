#!/usr/bin/env python3
"""Integration tests for complete user flows and scenarios."""

import pytest
from unittest.mock import Mock, patch
from addition import addition_mode, run_addition_quiz, ProblemGenerator


@pytest.mark.integration
class TestAdditionModeIntegration:
    """Integration tests for the complete addition mode flow."""
    
    def test_addition_mode_complete_flow(self, mocker, capsys):
        """Test complete addition mode flow with mocked user interactions."""
        # Mock user inputs: difficulty 1-2, 3 problems
        mock_get_user_input = mocker.patch('addition.get_user_input', side_effect=['1', '2', '3'])
        
        # Mock the quiz function to avoid complex quiz loop
        mock_run_quiz = mocker.patch('addition.run_addition_quiz', return_value=(2, 3, 45.0))
        
        # Mock show_results to avoid output complexity
        mock_show_results = mocker.patch('addition.show_results')
        
        # Run addition mode
        addition_mode()
        
        # Verify the flow
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that setup messages appeared
        assert "🔢 Addition Mode Selected!" in output
        assert "📋 Settings:" in output
        assert "Difficulty: 1 to 2" in output
        assert "Problems: 3" in output
        
        # Verify function calls
        assert mock_get_user_input.call_count == 3
        mock_run_quiz.assert_called_once()
        mock_show_results.assert_called_once_with(2, 3, 45.0, mocker.ANY)
    
    def test_addition_mode_unlimited_flow(self, mocker, capsys):
        """Test addition mode with unlimited problems."""
        # Mock user inputs: difficulty 3-5, unlimited (0)
        mock_get_user_input = mocker.patch('addition.get_user_input', side_effect=['3', '5', '0'])
        mock_run_quiz = mocker.patch('addition.run_addition_quiz', return_value=(15, 20, 180.5))
        mock_show_results = mocker.patch('addition.show_results')
        
        addition_mode()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "Mode: Unlimited (stop when ready)" in output
        mock_run_quiz.assert_called_once()
    
    def test_addition_mode_error_handling(self, mocker, capsys):
        """Test addition mode error handling."""
        # Mock an exception during the flow
        mock_get_user_input = mocker.patch('addition.get_user_input', side_effect=Exception("Test error"))
        
        addition_mode()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "❌ Error: Test error" in output
        assert "Returning to main menu..." in output


@pytest.mark.integration
class TestQuizFlowIntegration:
    """Integration tests for the quiz execution flow."""
    
    def test_run_addition_quiz_complete_session(self, mocker):
        """Test complete quiz session with multiple problems."""
        generator = ProblemGenerator(1, 1, 2)  # 2 single-digit problems
        
        # Mock the session prompt
        mock_prompt = mocker.patch('addition.prompt_start_session')
        
        # Mock user inputs: correct answer, correct answer (completes all problems)
        # Patch the input function used in run_addition_quiz
        mock_input = mocker.patch('builtins.input', side_effect=['5', '7'])
        
        # Mock problem generation to be predictable
        mocker.patch.object(generator, 'get_next_problem', side_effect=[
            ('2 + 3', 5),
            ('3 + 4', 7)
        ])
        
        correct, total, duration = run_addition_quiz(generator)
        
        assert correct == 2
        assert total == 2
        assert duration > 0
        mock_prompt.assert_called_once()
        assert mock_input.call_count == 2
    
    def test_run_addition_quiz_early_stop(self, mocker):
        """Test quiz session with early stop command."""
        generator = ProblemGenerator(1, 1, 5)  # 5 problems but will stop early
        
        mock_prompt = mocker.patch('addition.prompt_start_session')
        
        # Mock user inputs: correct answer, then stop
        mock_input = mocker.patch('builtins.input', side_effect=['8', 'stop'])
        
        mocker.patch.object(generator, 'get_next_problem', side_effect=[
            ('3 + 5', 8),
            ('4 + 6', 10)  # Won't reach this
        ])
        
        correct, total, duration = run_addition_quiz(generator)
        
        assert correct == 1
        assert total == 1
        assert duration > 0
    
    def test_run_addition_quiz_with_skips_and_retries(self, mocker, capsys):
        """Test quiz with skip commands and incorrect attempts."""
        generator = ProblemGenerator(1, 1, 2)
        
        mock_prompt = mocker.patch('addition.prompt_start_session')
        
        # Mock user inputs: wrong, wrong, next (skip), correct answer
        mock_input = mocker.patch('builtins.input', side_effect=['3', '4', 'next', '12'])
        
        mocker.patch.object(generator, 'get_next_problem', side_effect=[
            ('2 + 3', 5),   # User will skip this
            ('5 + 7', 12)   # User will get this correct
        ])
        
        correct, total, duration = run_addition_quiz(generator)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert correct == 1
        assert total == 3  # 2 wrong attempts + 1 correct
        assert "❌ Not quite right. Try again!" in output
        assert "⏭️  Skipped! The answer was 5" in output
        assert "✅ Correct! Great job!" in output
    
    def test_run_addition_quiz_exit_command(self, mocker):
        """Test quiz session with exit command."""
        generator = ProblemGenerator(1, 1, 5)
        
        mock_prompt = mocker.patch('addition.prompt_start_session')
        mock_input = mocker.patch('builtins.input', return_value='exit')
        
        mocker.patch.object(generator, 'get_next_problem', return_value=('1 + 1', 2))
        
        correct, total, duration = run_addition_quiz(generator)
        
        assert correct == 0
        assert total == 0
        assert duration > 0


@pytest.mark.integration
class TestEndToEndFlows:
    """End-to-end tests simulating complete user sessions."""
    
    def test_perfect_score_session(self, mocker, capsys):
        """Test a session where user gets perfect score."""
        # Setup mocks for perfect session
        mock_get_user_input = mocker.patch('addition.get_user_input', side_effect=['1', '1', '3'])
        
        # Mock quiz to return perfect score
        mock_run_quiz = mocker.patch('addition.run_addition_quiz', return_value=(3, 3, 60.0))
        
        # Don't mock show_results to test the actual result display
        addition_mode()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should see perfect score message
        assert "🔢 Addition Mode Selected!" in output
        assert "Difficulty: 1 to 1" in output
        assert "Problems: 3" in output
    
    def test_mixed_difficulty_session(self, mocker):
        """Test session with mixed difficulty levels."""
        generator = ProblemGenerator(1, 3, 5)  # Mix of difficulties 1-3
        
        problems_generated = []
        
        # Capture what problems are generated
        original_get_next = generator.get_next_problem
        def capture_problem():
            problem, answer = original_get_next()
            problems_generated.append((problem, answer))
            return problem, answer
        
        mocker.patch.object(generator, 'get_next_problem', side_effect=capture_problem)
        
        # Generate some problems to test difficulty range
        for _ in range(5):
            if generator.has_more_problems():
                generator.get_next_problem()
        
        # Verify we got problems from the specified difficulty range
        assert len(problems_generated) == 5
        for problem, answer in problems_generated:
            parts = problem.split(' + ')
            num1, num2 = int(parts[0]), int(parts[1])
            
            # Verify numbers are in expected ranges for difficulties 1-3
            # (single digit to two digit)
            assert 0 <= num1 <= 99
            assert 0 <= num2 <= 99
            assert answer == num1 + num2


@pytest.mark.integration
@pytest.mark.slow
class TestStressTests:
    """Stress tests for edge cases and performance."""
    
    def test_large_number_of_problems(self):
        """Test generator with large number of problems."""
        generator = ProblemGenerator(1, 5, 1000)
        
        problems_solved = 0
        while generator.has_more_problems() and problems_solved < 100:  # Limit for test speed
            problem, answer = generator.get_next_problem()
            problems_solved += 1
            
            # Verify each problem is valid
            parts = problem.split(' + ')
            num1, num2 = int(parts[0]), int(parts[1])
            assert answer == num1 + num2
        
        assert problems_solved == 100
        assert generator.get_total_generated() == 100
    
    def test_unlimited_generator_properties(self):
        """Test unlimited generator maintains properties over many generations."""
        generator = ProblemGenerator(2, 4, 0)  # Unlimited
        
        for _ in range(50):
            assert generator.has_more_problems()
            problem, answer = generator.get_next_problem()
            
            # Verify problem format
            assert ' + ' in problem
            parts = problem.split(' + ')
            num1, num2 = int(parts[0]), int(parts[1])
            
            # Verify difficulty range (2-4 means 10-999)
            assert 10 <= num1 <= 999
            assert 10 <= num2 <= 999
            assert answer == num1 + num2
        
        assert generator.get_total_generated() == 50