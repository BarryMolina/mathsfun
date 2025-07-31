"""Tests for MathFactService with SM-2 spaced repetition."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.services.math_fact_service import MathFactService
from src.domain.models.math_fact_performance import MathFactPerformance
from src.domain.models.math_fact_attempt import MathFactAttempt


class TestMathFactService:
    """Test MathFactService functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository):
        """Create a MathFactService instance with mock repository."""
        return MathFactService(mock_repository)

    def test_track_attempt_new_fact(self, service, mock_repository):
        """Test tracking an attempt for a new fact."""
        # Mock repository to return None (new fact)
        mock_repository.get_user_fact_performance.return_value = None
        mock_repository.upsert_fact_performance_with_attempt.return_value = Mock()

        result = service.track_attempt(
            user_id="user123",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2500,
            incorrect_attempts_in_session=0
        )

        # Verify repository calls
        mock_repository.get_user_fact_performance.assert_called_once_with("user123", "7+8")
        mock_repository.upsert_fact_performance_with_attempt.assert_called_once()
        assert result is not None

    def test_track_attempt_existing_fact(self, service, mock_repository):
        """Test tracking an attempt for an existing fact."""
        # Create existing performance
        existing_performance = MathFactPerformance.create_new("user123", "7+8")
        # Simulate existing performance by updating internal state
        existing_performance.total_attempts = 3
        existing_performance.correct_attempts = 2
        existing_performance.total_response_time_ms = 6000  # Set total time instead of average
        existing_performance.repetition_number = 1
        existing_performance.easiness_factor = Decimal("2.60")

        mock_repository.get_user_fact_performance.return_value = existing_performance
        mock_repository.upsert_fact_performance_with_attempt.return_value = existing_performance

        result = service.track_attempt(
            user_id="user123",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2000,
            incorrect_attempts_in_session=1
        )

        # Verify repository calls
        mock_repository.get_user_fact_performance.assert_called_once_with("user123", "7+8")
        mock_repository.upsert_fact_performance_with_attempt.assert_called_once()
        assert result is not None

    def test_track_attempt_incorrect_answer(self, service, mock_repository):
        """Test tracking an incorrect attempt."""
        mock_repository.get_user_fact_performance.return_value = None
        mock_repository.upsert_fact_performance_with_attempt.return_value = Mock()

        result = service.track_attempt(
            user_id="user123",
            operand1=9,
            operand2=6,
            user_answer=14,  # Wrong answer
            correct_answer=15,
            is_correct=False,
            response_time_ms=5000,
            incorrect_attempts_in_session=2
        )

        # Verify the attempt was processed
        call_args = mock_repository.upsert_fact_performance_with_attempt.call_args
        performance_arg = call_args[0][0]
        attempt_arg = call_args[0][1]

        assert not attempt_arg.is_correct
        assert attempt_arg.user_answer == 14
        assert attempt_arg.incorrect_attempts_in_session == 2
        assert result is not None

    def test_track_attempt_skipped(self, service, mock_repository):
        """Test tracking a skipped attempt."""
        mock_repository.get_user_fact_performance.return_value = None
        mock_repository.upsert_fact_performance_with_attempt.return_value = Mock()

        result = service.track_attempt(
            user_id="user123",
            operand1=8,
            operand2=7,
            user_answer=None,  # Skipped
            correct_answer=15,
            is_correct=False,
            response_time_ms=1000,
            incorrect_attempts_in_session=0
        )

        # Verify the attempt was processed as skipped
        call_args = mock_repository.upsert_fact_performance_with_attempt.call_args
        attempt_arg = call_args[0][1]

        assert attempt_arg.user_answer is None
        assert not attempt_arg.is_correct
        # For skipped with no incorrect attempts, would still be perfect time grade (< 2000ms)
        assert attempt_arg.sm2_grade == 5  # Fast skip still gets high grade
        assert result is not None

    def test_get_facts_due_for_review(self, service, mock_repository):
        """Test getting facts due for review."""
        # Mock facts due for review
        due_facts = [
            MathFactPerformance.create_new("user123", "7+8"),
            MathFactPerformance.create_new("user123", "9+6"),
        ]
        mock_repository.get_facts_due_for_review.return_value = due_facts

        result = service.get_facts_due_for_review("user123", limit=10)

        mock_repository.get_facts_due_for_review.assert_called_once_with("user123", 10)
        assert result == due_facts

    def test_get_all_user_performances(self, service, mock_repository):
        """Test getting all user performances."""
        performances = [
            MathFactPerformance.create_new("user123", "7+8"),
            MathFactPerformance.create_new("user123", "9+6"),
            MathFactPerformance.create_new("user123", "5+5"),
        ]
        mock_repository.get_all_user_performances.return_value = performances

        result = service.get_all_user_performances("user123")

        mock_repository.get_all_user_performances.assert_called_once_with("user123")
        assert result == performances

    def test_get_weak_facts(self, service, mock_repository):
        """Test getting weak facts."""
        # Mock facts due for review (this is called first in the service method)
        due_facts = [
            MathFactPerformance.create_new("user123", "5+5"),  # Due for review
        ]
        mock_repository.get_facts_due_for_review.return_value = due_facts
        
        # Mock additional weak facts
        weak_facts = [
            MathFactPerformance.create_new("user123", "9+8"),  # Might be difficult
            MathFactPerformance.create_new("user123", "7+9"),
        ]
        mock_repository.get_weak_facts.return_value = weak_facts

        result = service.get_weak_facts("user123", (1, 10), 5)

        # Should get facts due for review first, then additional weak facts
        mock_repository.get_facts_due_for_review.assert_called_once_with("user123", 5)
        mock_repository.get_weak_facts.assert_called_once_with("user123", (1, 10), 4)  # 5 - 1 due fact
        assert len(result) == 3  # 1 due fact + 2 weak facts (only 2 available)
        assert result[0].fact_key == "5+5"  # Due fact comes first
        assert result[1].fact_key == "9+8"  # Weak facts follow
        assert result[2].fact_key == "7+9"

    def test_analyze_session_performance_empty(self, service, mock_repository):
        """Test analyzing empty session performance."""
        mock_repository.batch_upsert_fact_performances.return_value = []
        mock_repository.get_facts_due_for_review.return_value = []

        result = service.analyze_session_performance("user123", [])

        assert result["facts_practiced"] == []
        assert result["new_facts_learned"] == []
        assert result["facts_due_for_review"] == 0

    def test_analyze_session_performance_with_attempts(self, service, mock_repository):
        """Test analyzing session performance with attempts."""
        session_attempts = [
            (7, 8, True, 2500, 0),   # Correct on first try
            (9, 6, False, 5000, 2),  # Incorrect after 2 attempts
            (5, 5, True, 1500, 1),   # Correct after 1 mistake
        ]

        # Mock that no existing performances exist (all new facts)
        mock_repository.get_user_fact_performance.return_value = None
        
        # Mock successful track_attempt calls
        mock_performances = [
            MathFactPerformance.create_new("user123", "7+8"),
            MathFactPerformance.create_new("user123", "9+6"),
            MathFactPerformance.create_new("user123", "5+5"),
        ]
        mock_repository.upsert_fact_performance_with_attempt.side_effect = mock_performances
        
        # Mock facts due for review
        mock_repository.get_facts_due_for_review.return_value = [mock_performances[1]]  # Only 9+6 still due

        result = service.analyze_session_performance("user123", session_attempts)

        # Verify individual track_attempt calls were made (not batch)
        assert mock_repository.upsert_fact_performance_with_attempt.call_count == 3
        assert len(result["facts_practiced"]) == 3
        assert result["new_facts_learned"] == ["7+8", "9+6", "5+5"]  # All new facts
        assert result["facts_due_for_review"] == 1

    def test_get_performance_summary_empty(self, service, mock_repository):
        """Test getting performance summary for user with no facts."""
        mock_repository.get_all_user_performances.return_value = []

        result = service.get_performance_summary("user123")

        assert result["total_facts"] == 0
        assert result["average_accuracy"] == 0.0
        assert result["average_ease_factor"] == 2.5
        assert result["facts_by_interval"] == {}

    def test_get_performance_summary_with_facts(self, service, mock_repository):
        """Test getting performance summary with facts."""
        # Create performances with different stats
        perf1 = MathFactPerformance.create_new("user123", "7+8")
        perf1.total_attempts = 10
        perf1.correct_attempts = 8
        perf1.easiness_factor = Decimal("2.8")
        perf1.interval_days = 1

        perf2 = MathFactPerformance.create_new("user123", "9+6")
        perf2.total_attempts = 5
        perf2.correct_attempts = 3
        perf2.easiness_factor = Decimal("2.2")
        perf2.interval_days = 6

        perf3 = MathFactPerformance.create_new("user123", "5+5")
        perf3.total_attempts = 8
        perf3.correct_attempts = 8
        perf3.easiness_factor = Decimal("3.0")
        perf3.interval_days = 6

        performances = [perf1, perf2, perf3]
        mock_repository.get_all_user_performances.return_value = performances

        result = service.get_performance_summary("user123")

        assert result["total_facts"] == 3
        # Average accuracy: (80% + 60% + 100%) / 3 = 80%
        assert result["average_accuracy"] == 80.0
        # Average ease: (2.8 + 2.2 + 3.0) / 3 = 2.67 (rounded)
        assert abs(result["average_ease_factor"] - 2.67) < 0.01
        # Interval distribution: 1 fact at 1 day, 2 facts at 6 days
        assert result["facts_by_interval"] == {1: 1, 6: 2}

    def test_track_attempt_repository_failure(self, service, mock_repository):
        """Test handling repository failure when tracking attempt."""
        mock_repository.get_user_fact_performance.return_value = None
        mock_repository.upsert_fact_performance_with_attempt.return_value = None  # Failure

        result = service.track_attempt(
            user_id="user123",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2500
        )

        assert result is None

    def test_sm2_grade_calculation_in_service(self, service, mock_repository):
        """Test that SM-2 grade calculation works correctly in service context."""
        mock_repository.get_user_fact_performance.return_value = None
        
        # Mock to capture what gets passed to the repository
        captured_performance = None
        captured_attempt = None
        
        def capture_args(performance, attempt):
            nonlocal captured_performance, captured_attempt
            captured_performance = performance
            captured_attempt = attempt
            return performance
        
        mock_repository.upsert_fact_performance_with_attempt.side_effect = capture_args

        # Track a fast, correct attempt
        service.track_attempt(
            user_id="user123",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=1500,  # Fast response
            incorrect_attempts_in_session=0
        )

        # Verify SM-2 grade was calculated correctly
        assert captured_attempt.sm2_grade == 5  # Should be perfect recall
        assert captured_performance.repetition_number == 1
        assert captured_performance.interval_days == 1

    @pytest.mark.parametrize("response_time,incorrect_attempts,expected_grade", [
        (1000, 0, 5),   # Perfect (< 2000ms, no errors)
        (2500, 0, 4),   # Good (2000-3000ms, no errors)
        (4000, 0, 3),   # Satisfactory (>= 3000ms, no errors)
        (2500, 1, 2),   # Easy to remember after error (< 3000ms, 1 error)
        (4000, 1, 1),   # Familiar but slow after error (>= 3000ms, 1 error)
        (10000, 5, 0),  # Blackout (2+ errors)
    ])
    def test_grade_calculation_scenarios(self, service, mock_repository, response_time, incorrect_attempts, expected_grade):
        """Test various grade calculation scenarios in service."""
        mock_repository.get_user_fact_performance.return_value = None
        
        captured_attempt = None
        def capture_attempt(performance, attempt):
            nonlocal captured_attempt
            captured_attempt = attempt
            return performance
        
        mock_repository.upsert_fact_performance_with_attempt.side_effect = capture_attempt

        service.track_attempt(
            user_id="user123",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=response_time,
            incorrect_attempts_in_session=incorrect_attempts
        )

        assert captured_attempt.sm2_grade == expected_grade