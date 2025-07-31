"""Tests for MathFactPerformance model with SM-2 algorithm."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.domain.models.math_fact_performance import MathFactPerformance


class TestMathFactPerformance:
    """Test SM-2 spaced repetition functionality in MathFactPerformance."""

    def test_create_new_performance(self):
        """Test creating a new math fact performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        assert performance.user_id == "user123"
        assert performance.fact_key == "7+8"
        assert performance.total_attempts == 0
        assert performance.correct_attempts == 0
        assert performance.average_response_time_ms == 0
        assert performance.repetition_number == 0
        assert performance.easiness_factor == Decimal("2.50")
        assert performance.interval_days == 1
        assert performance.next_review_date is not None  # Set to tomorrow initially
        assert performance.last_attempted is None

    def test_update_performance_correct(self):
        """Test updating performance with correct answer."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        performance.update_performance(is_correct=True, response_time_ms=2500)

        assert performance.total_attempts == 1
        assert performance.correct_attempts == 1
        assert performance.average_response_time_ms == 2500
        assert performance.last_attempted is not None

    def test_update_performance_incorrect(self):
        """Test updating performance with incorrect answer."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        performance.update_performance(is_correct=False, response_time_ms=5000)

        assert performance.total_attempts == 1
        assert performance.correct_attempts == 0
        assert (
            performance.average_response_time_ms == 0
        )  # No time tracked for incorrect attempts

    def test_update_performance_multiple_attempts(self):
        """Test updating performance with multiple attempts."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # First attempt: correct, 2000ms
        performance.update_performance(is_correct=True, response_time_ms=2000)
        # Second attempt: incorrect, 4000ms (not counted in average)
        performance.update_performance(is_correct=False, response_time_ms=4000)
        # Third attempt: correct, 3000ms
        performance.update_performance(is_correct=True, response_time_ms=3000)

        assert performance.total_attempts == 3
        assert performance.correct_attempts == 2
        # Average: (2000 + 3000) / 2 = 2500 (only correct attempts)
        assert performance.average_response_time_ms == 2500

    def test_calculate_sm2_grade_excellent(self):
        """Test SM-2 grade calculation for excellent performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Very fast response, no incorrect attempts
        grade = performance.calculate_sm2_grade(
            response_time_ms=1000, incorrect_attempts=0
        )
        assert grade == 5  # Perfect recall

    def test_calculate_sm2_grade_good(self):
        """Test SM-2 grade calculation for good performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Fast response, no incorrect attempts
        grade = performance.calculate_sm2_grade(
            response_time_ms=2500, incorrect_attempts=0
        )
        assert grade == 4  # Good recall

    def test_calculate_sm2_grade_medium(self):
        """Test SM-2 grade calculation for medium performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Medium response, no incorrect attempts
        grade = performance.calculate_sm2_grade(
            response_time_ms=4000, incorrect_attempts=0
        )
        assert grade == 3  # Satisfactory recall

    def test_calculate_sm2_grade_poor(self):
        """Test SM-2 grade calculation for poor performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Slow response, with 2+ incorrect attempts
        grade = performance.calculate_sm2_grade(
            response_time_ms=8000, incorrect_attempts=2
        )
        assert grade == 0  # Total blackout (2+ incorrect attempts)

    def test_calculate_sm2_grade_blackout(self):
        """Test SM-2 grade calculation for blackout (many errors)."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Very slow response, many incorrect attempts
        grade = performance.calculate_sm2_grade(
            response_time_ms=12000, incorrect_attempts=5
        )
        assert grade == 0  # Complete blackout

    def test_apply_sm2_algorithm_first_repetition_good(self):
        """Test SM-2 algorithm for first repetition with good performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Apply grade 4 (good performance)
        performance.apply_sm2_algorithm(grade=4)

        assert performance.repetition_number == 1
        assert performance.interval_days == 1
        # EF calculation: 2.5 + (0.1 - (5-4) * (0.08 + (5-4) * 0.02)) = 2.5 + (0.1 - 0.1) = 2.5
        assert performance.easiness_factor == Decimal("2.50")
        assert performance.next_review_date is not None

    def test_apply_sm2_algorithm_second_repetition_good(self):
        """Test SM-2 algorithm for second repetition with good performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.repetition_number = 1
        performance.interval_days = 1

        # Apply grade 4 (good performance)
        performance.apply_sm2_algorithm(grade=4)

        assert performance.repetition_number == 2
        assert performance.interval_days == 6
        # EF stays same: 2.5 + (0.1 - (5-4) * (0.08 + (5-4) * 0.02)) = 2.5
        assert performance.easiness_factor == Decimal("2.50")

    def test_apply_sm2_algorithm_third_repetition_good(self):
        """Test SM-2 algorithm for third repetition with good performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.repetition_number = 2
        performance.interval_days = 6
        performance.easiness_factor = Decimal("2.60")

        # Apply grade 4 (good performance)
        performance.apply_sm2_algorithm(grade=4)

        assert performance.repetition_number == 3
        # 6 * 2.60 = 15.6, rounded down to 15
        assert performance.interval_days == 15
        # EF stays same: 2.6 + (0.1 - (5-4) * (0.08 + (5-4) * 0.02)) = 2.6
        assert performance.easiness_factor == Decimal("2.60")

    def test_apply_sm2_algorithm_poor_performance_reset(self):
        """Test SM-2 algorithm reset for poor performance."""
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.repetition_number = 5
        performance.interval_days = 30
        performance.easiness_factor = Decimal("3.00")

        # Apply grade 2 (poor performance)
        performance.apply_sm2_algorithm(grade=2)

        # Should reset to beginning
        assert performance.repetition_number == 0
        assert performance.interval_days == 1
        # Ease factor should decrease: 3.0 + (0.1 - 3 * (0.08 + 3 * 0.02)) = 3.0 - 0.32 = 2.68
        assert performance.easiness_factor == Decimal("2.68")

    def test_apply_sm2_algorithm_easiness_factor_bounds(self):
        """Test that easiness factor stays within bounds."""
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.easiness_factor = Decimal("1.30")  # At minimum

        # Apply terrible grade (should not go below 1.3)
        performance.apply_sm2_algorithm(grade=0)
        assert performance.easiness_factor >= Decimal("1.30")

        # Reset to high value
        performance.easiness_factor = Decimal("4.00")  # At maximum

        # Apply excellent grade (should not go above 4.0)
        performance.apply_sm2_algorithm(grade=5)
        assert performance.easiness_factor <= Decimal("4.00")

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        original = MathFactPerformance.create_new("user123", "7+8")
        original.update_performance(True, 2500)
        original.apply_sm2_algorithm(4)

        # Convert to dict and back
        data = original.to_dict()
        restored = MathFactPerformance.from_dict(data)

        assert restored.user_id == original.user_id
        assert restored.fact_key == original.fact_key
        assert restored.total_attempts == original.total_attempts
        assert restored.correct_attempts == original.correct_attempts
        assert restored.average_response_time_ms == original.average_response_time_ms
        assert restored.repetition_number == original.repetition_number
        assert restored.easiness_factor == original.easiness_factor
        assert restored.interval_days == original.interval_days

    @pytest.mark.parametrize(
        "response_time,incorrect_attempts,expected_grade",
        [
            (800, 0, 5),  # Perfect (< 2000ms, no errors)
            (1500, 0, 5),  # Perfect (< 2000ms, no errors)
            (2500, 0, 4),  # Good (2000-3000ms, no errors)
            (3000, 0, 3),  # Satisfactory (>= 3000ms, no errors)
            (4000, 0, 3),  # Satisfactory (>= 3000ms, no errors)
            (2500, 1, 2),  # Easy to remember after error (< 3000ms, 1 error)
            (4000, 1, 1),  # Familiar but slow after error (>= 3000ms, 1 error)
            (2000, 2, 0),  # Blackout (2+ errors)
            (10000, 3, 0),  # Blackout (2+ errors)
            (15000, 5, 0),  # Complete blackout (2+ errors)
        ],
    )
    def test_sm2_grade_calculation_scenarios(
        self, response_time, incorrect_attempts, expected_grade
    ):
        """Test various grade calculation scenarios."""
        performance = MathFactPerformance.create_new("user123", "7+8")
        grade = performance.calculate_sm2_grade(response_time, incorrect_attempts)
        assert grade == expected_grade

    def test_sm2_algorithm_progression_sequence(self):
        """Test a realistic SM-2 progression sequence."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # Session 1: Good performance
        grade1 = performance.calculate_sm2_grade(2000, 0)  # Grade 4
        performance.apply_sm2_algorithm(grade1)

        assert performance.repetition_number == 1
        assert performance.interval_days == 1
        review_date_1 = performance.next_review_date

        # Session 2: Good performance again
        grade2 = performance.calculate_sm2_grade(1800, 0)  # Grade 4
        performance.apply_sm2_algorithm(grade2)

        assert performance.repetition_number == 2
        assert performance.interval_days == 6
        assert performance.next_review_date > review_date_1

        # Session 3: Excellent performance
        grade3 = performance.calculate_sm2_grade(1200, 0)  # Grade 5
        performance.apply_sm2_algorithm(grade3)

        assert performance.repetition_number == 3
        assert performance.interval_days > 6  # Should be around 15+ days
        assert performance.easiness_factor > Decimal("2.50")  # Should have increased

        # Session 4: Poor performance (should reset)
        grade4 = performance.calculate_sm2_grade(8000, 3)  # Grade 1
        performance.apply_sm2_algorithm(grade4)

        assert performance.repetition_number == 0  # Reset
        assert performance.interval_days == 1  # Reset
        # Ease factor should have decreased but stayed >= 1.3

    def test_accuracy_calculation(self):
        """Test accuracy calculation property."""
        performance = MathFactPerformance.create_new("user123", "7+8")

        # No attempts yet
        assert performance.accuracy == 0.0

        # 3 correct out of 5 attempts
        performance.total_attempts = 5
        performance.correct_attempts = 3
        assert performance.accuracy == 60.0

        # Perfect accuracy
        performance.correct_attempts = 5
        assert performance.accuracy == 100.0
