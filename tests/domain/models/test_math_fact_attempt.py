"""Tests for MathFactAttempt model."""

import pytest
from datetime import datetime
from src.domain.models.math_fact_attempt import MathFactAttempt


class TestMathFactAttempt:
    """Test MathFactAttempt model functionality."""

    def test_create_new_attempt_correct(self):
        """Test creating a new correct attempt."""
        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="7+8",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2500,
            incorrect_attempts_in_session=0,
            sm2_grade=4,
        )

        assert attempt.user_id == "user123"
        assert attempt.fact_key == "7+8"
        assert attempt.operand1 == 7
        assert attempt.operand2 == 8
        assert attempt.user_answer == 15
        assert attempt.correct_answer == 15
        assert attempt.is_correct is True
        assert attempt.response_time_ms == 2500
        assert attempt.incorrect_attempts_in_session == 0
        assert attempt.sm2_grade == 4
        assert isinstance(attempt.attempted_at, datetime)

    def test_create_new_attempt_incorrect(self):
        """Test creating a new incorrect attempt."""
        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="9+6",
            operand1=9,
            operand2=6,
            user_answer=14,  # Wrong answer
            correct_answer=15,
            is_correct=False,
            response_time_ms=5000,
            incorrect_attempts_in_session=2,
            sm2_grade=1,
        )

        assert attempt.user_answer == 14
        assert attempt.correct_answer == 15
        assert attempt.is_correct is False
        assert attempt.incorrect_attempts_in_session == 2
        assert attempt.sm2_grade == 1

    def test_create_new_attempt_skipped(self):
        """Test creating an attempt for a skipped problem."""
        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="8+7",
            operand1=8,
            operand2=7,
            user_answer=None,  # Skipped
            correct_answer=15,
            is_correct=False,
            response_time_ms=1000,
            incorrect_attempts_in_session=1,
            sm2_grade=0,
        )

        assert attempt.user_answer is None
        assert attempt.correct_answer == 15
        assert attempt.is_correct is False
        assert attempt.sm2_grade == 0

    def test_create_new_attempt_with_current_timestamp(self):
        """Test creating an attempt uses current timestamp."""
        before_time = datetime.now()

        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="5+5",
            operand1=5,
            operand2=5,
            user_answer=10,
            correct_answer=10,
            is_correct=True,
            response_time_ms=1500,
        )

        after_time = datetime.now()

        # Verify timestamp is between before and after
        assert before_time <= attempt.attempted_at <= after_time

    def test_to_dict_and_from_dict_correct(self):
        """Test serialization and deserialization of correct attempt."""
        original = MathFactAttempt.create_new(
            user_id="user456",
            fact_key="6+9",
            operand1=6,
            operand2=9,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=3000,
            incorrect_attempts_in_session=1,
            sm2_grade=3,
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = MathFactAttempt.from_dict(data)

        assert restored.user_id == original.user_id
        assert restored.fact_key == original.fact_key
        assert restored.operand1 == original.operand1
        assert restored.operand2 == original.operand2
        assert restored.user_answer == original.user_answer
        assert restored.correct_answer == original.correct_answer
        assert restored.is_correct == original.is_correct
        assert restored.response_time_ms == original.response_time_ms
        assert (
            restored.incorrect_attempts_in_session
            == original.incorrect_attempts_in_session
        )
        assert restored.sm2_grade == original.sm2_grade
        assert restored.attempted_at == original.attempted_at

    def test_to_dict_and_from_dict_skipped(self):
        """Test serialization and deserialization of skipped attempt."""
        original = MathFactAttempt.create_new(
            user_id="user789",
            fact_key="12+8",
            operand1=12,
            operand2=8,
            user_answer=None,  # Skipped
            correct_answer=20,
            is_correct=False,
            response_time_ms=2000,
            incorrect_attempts_in_session=0,
            sm2_grade=0,
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = MathFactAttempt.from_dict(data)

        assert restored.user_answer is None
        assert restored.is_correct is False
        assert restored.sm2_grade == 0

    @pytest.mark.parametrize(
        "user_answer,correct_answer,expected_correct",
        [
            (15, 15, True),  # Correct answer
            (14, 15, False),  # Wrong answer
            (16, 15, False),  # Wrong answer
            (None, 15, False),  # Skipped
        ],
    )
    def test_correctness_scenarios(self, user_answer, correct_answer, expected_correct):
        """Test various correctness scenarios."""
        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="7+8",
            operand1=7,
            operand2=8,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=expected_correct,
            response_time_ms=2000,
        )

        assert attempt.is_correct == expected_correct

    def test_response_time_scenarios(self):
        """Test various response time scenarios."""
        # Very fast response
        fast_attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="2+2",
            operand1=2,
            operand2=2,
            user_answer=4,
            correct_answer=4,
            is_correct=True,
            response_time_ms=800,
        )

        assert fast_attempt.response_time_ms == 800

        # Very slow response
        slow_attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="9+9",
            operand1=9,
            operand2=9,
            user_answer=18,
            correct_answer=18,
            is_correct=True,
            response_time_ms=15000,
        )

        assert slow_attempt.response_time_ms == 15000

    def test_sm2_grade_scenarios(self):
        """Test various SM-2 grade scenarios."""
        grades = [0, 1, 2, 3, 4, 5]

        for grade in grades:
            attempt = MathFactAttempt.create_new(
                user_id="user123",
                fact_key="5+7",
                operand1=5,
                operand2=7,
                user_answer=12,
                correct_answer=12,
                is_correct=True,
                response_time_ms=2000,
                sm2_grade=grade,
            )

            assert attempt.sm2_grade == grade

    def test_incorrect_attempts_scenarios(self):
        """Test various incorrect attempts in session scenarios."""
        scenarios = [0, 1, 2, 3, 5, 10]

        for incorrect_count in scenarios:
            attempt = MathFactAttempt.create_new(
                user_id="user123",
                fact_key="8+4",
                operand1=8,
                operand2=4,
                user_answer=12,
                correct_answer=12,
                is_correct=True,
                response_time_ms=3000,
                incorrect_attempts_in_session=incorrect_count,
            )

            assert attempt.incorrect_attempts_in_session == incorrect_count
